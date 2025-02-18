import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from typing import List
from datetime import datetime, timezone
import logfire
from models import TagResponse, TopicSummary, Image
# from db import is_image_downloaded, get_image_count, remove_oldest_images, add_image, get_last_successful_fetch, update_last_successful_fetch
import db

logfire.configure()

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv('DISCOURSE_API_KEY')
api_username = os.getenv('DISCOURSE_API_USERNAME')
base_url = os.getenv('DISCOURSE_BASE_URL')
tag_name = os.getenv('DISCOURSE_TAG')
batch_size = int(os.getenv('BATCH_SIZE', '20'))
image_limit = int(os.getenv('IMAGE_LIMIT'))
image_dir = os.getenv('IMAGE_DIR')

headers = {
    'Api-Key': api_key,
    'Api-Username': api_username
}

def get_tagged_topics(base_url, tag_name):
    """
    Fetch topics with specified tag from Discourse
    
    Args:
        base_url (str): Base URL of Discourse instance (from config)
        tag_name (str): Name of tag to search for (from config)
    
    Returns:
        list: List of topic data dictionaries
    """
    
    url = f"{base_url}/tag/{tag_name}.json"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tag_data = TagResponse(**response.json())
        topics = tag_data.topic_list.topics
        
        # Filter based on last successful fetch
        last_fetch = db.get_last_successful_fetch()
        if last_fetch:
            topics = [t for t in topics if t.bumped_at > last_fetch]
            
        logfire.notice('filtered_topics', count=len(topics))
        return topics
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching tagged topics: {e}")
        return []


def process_topics(topics: List[TopicSummary]) -> List[Image]:

    all_images = []
    
    # Convert topics list to chunks based on batch_size
    topic_chunks = [topics[i:i + batch_size] for i in range(0, len(topics), batch_size)]
    
    for chunk in topic_chunks:
        for topic in chunk:
            try:
                print(f"Processing topic {topic.id}: {topic.title}")
                cooked_html = fetch_topic_content(topic.id)
                images = extract_original_images(cooked_html)
                all_images.extend(images)
                # Maybe add some basic logging here
            except Exception as e:
                print(f"Error processing topic {topic.id}: {e}")
                continue
        
        # If there are more chunks to process, maybe add a small delay
        if chunk != topic_chunks[-1]:
            time.sleep(2)  # Arbitrary 2-second delay between batches
    
    logfire.notice('All images', all_images=all_images)
    return all_images


def fetch_topic_content(topic_id: int) -> str:
    """Fetch the cooked HTML content for a specific topic"""
    
    url = f"{base_url}/t/{topic_id}.json"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # The cooked content is in the first post
    post_content = response.json().get('post_stream', {}).get('posts', [{}])[0]
    return post_content.get('cooked', '')


def extract_original_images(cooked_html):
    soup = BeautifulSoup(cooked_html, 'html.parser')
    images = set()  # Using a set for initial deduplication
    
    # Find all elements with href or src attributes
    for element in soup.find_all(['a', 'img']):
        url = element.get('href') or element.get('src')
        if url and '/default/original/' in url:
            if url.startswith('//'):
                url = 'https:' + url
            
            # Extract hash from URL
            hash_match = re.search(r'/(\w{40})\.\w+$', url)
            if hash_match:
                file_hash = hash_match.group(1)
                images.add((url, file_hash))
    
    # Convert set to list of dictionaries
    return [
        {
            'url': url,
            'hash': file_hash
        }
        for url, file_hash in images
    ]


def download_images(images: List[dict]):
    """Download new images, managing storage limits"""
    
    # Filter out images we already have
    new_images = [img for img in images 
                 if not db.is_image_downloaded(img['hash'])]
    
    if not new_images:
        print("No new images to download")
        return
    
    # Check if we need to make room
    current_count = db.get_image_count()
    if current_count + len(new_images) > image_limit:
        to_remove = (current_count + len(new_images)) - image_limit
        db.remove_oldest_images(to_remove)
    
    # Download new images
    for img in new_images:
        try:
            # Construct filename (maybe hash + original extension?)
            ext = os.path.splitext(img['url'])[1]
            filename = f"{img['hash']}{ext}"
            filepath = os.path.join(image_dir, filename)
            
            response = requests.get(img['url'], headers=headers)
            response.raise_for_status()
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Update database
            db.add_image(
                hash=img['hash'],
                filename=filename,
                url=img['url'],
                downloaded_at=datetime.now(timezone.utc)
            )
            
            print(f"Downloaded: {filename}")
            
        except Exception as e:
            print(f"Error downloading {img['url']}: {e}")
            continue


def main():
    tagged_topics = get_tagged_topics(base_url, tag_name)
    
    if not tagged_topics:
        logfire.notice('No new topics since last fetch, exiting')
        return
        
    image_list = process_topics(tagged_topics)
    
    if not image_list:
        logfire.notice('No new images found in topics, exiting')
        return
        
    download_images(image_list)
    db.update_last_successful_fetch(datetime.now(timezone.utc))

if __name__ == "__main__":
    main()