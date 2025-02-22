import os
import sys
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
from typing import List
from datetime import datetime, timezone
from models import TagResponse, TopicSummary, Image
import db
from logging_config import setup_logging

logger = setup_logging()

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv('DISCOURSE_API_KEY')
api_username = os.getenv('DISCOURSE_API_USERNAME')
base_url = os.getenv('DISCOURSE_BASE_URL')
tag_name = os.getenv('DISCOURSE_TAG')
discourse_admin = os.getenv('DISCOURSE_NOTIFICATION_USER')
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
    """

    url = f"{base_url}/tag/{tag_name}.json"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tag_data = TagResponse(**response.json())
        topics = tag_data.topic_list.topics
        
        last_fetch = db.get_last_successful_fetch()
        if last_fetch:
            topics = [t for t in topics if t.bumped_at > last_fetch]
            
        logger.info(f'Found {len(topics)} new topics since last fetch')
        return topics
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching tagged topics: {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"Error parsing response data: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_tagged_topics: {str(e)}")
        raise


def process_topics(topics: List[TopicSummary]) -> List[Image]:
    """
    Process a list of topics and extracts all images from the first post. Topics are processed in batches.
    """

    all_images = []
    topic_chunks = [topics[i:i + batch_size] for i in range(0, len(topics), batch_size)]
    
    for chunk in topic_chunks:
        for topic in chunk:
            try:
                logger.info(f"Processing topic {topic.id}: {topic.title}")
                cooked_html = fetch_topic_content(topic.id)
                images = extract_original_images(cooked_html)
                all_images.extend(images)
                logger.info(f"Found {len(images)} images in topic {topic.id}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error processing topic {topic.id}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error processing topic {topic.id}: {str(e)}")
                continue
    
    logger.info(f'Found total of {len(all_images)} images across all topics')
    return all_images


def fetch_topic_content(topic_id: int) -> str:
    """
    Fetch the cooked HTML content for a specific topic
    """

    url = f"{base_url}/t/{topic_id}.json"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        post_content = response.json().get('post_stream', {}).get('posts', [{}])[0]
        content = post_content.get('cooked', '')
        if not content:
            logger.warning(f"Empty content returned for topic {topic_id}")
        return content
        
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        logger.error(f"Error fetching topic {topic_id}: {str(e)}")
        return None


def extract_original_images(cooked_html):
    """
    Extract original image URLs and hashes from cooked HTML content
    """

    try:
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
        image_list = [
            {
                'url': url,
                'hash': file_hash
            }
            for url, file_hash in images
        ]
        
        logger.debug(f"Extracted {len(image_list)} unique images from HTML content")
        return image_list
        
    except Exception as e:
        logger.error(f"Error extracting images from HTML: {str(e)}")
        return []


def download_images(images: List[dict]):
    """
    Download new images, managing storage limits
    
    Args:
        images: List of dictionaries containing image information
        
    Raises:
        SystemError: If too many consecutive downloads fail
        requests.exceptions.RequestException: For network/API errors
        IOError: For file system errors
        sqlite3.Error: For database errors
    """
    failed_downloads = []
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 3

    new_images = [img for img in images 
                 if not db.is_image_downloaded(img['hash'])]
    
    if not new_images:
        logger.info("No new images to download")
        return
    
    logger.info("Found %d new images to download", len(new_images))
    
    current_count = db.get_image_count()
    if current_count + len(new_images) > image_limit:
        to_remove = (current_count + len(new_images)) - image_limit
        logger.warning("Need to remove %d images to stay under limit", to_remove)
        db.remove_oldest_images(to_remove)
    
    for img in new_images:
        try:
            ext = os.path.splitext(img['url'])[1]
            filename = f"{img['hash']}{ext}"
            filepath = os.path.join(image_dir, filename)
            
            logger.debug("Downloading %s to %s", img['url'], filepath)
            
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
            
            logger.info("Successfully downloaded: %s", filename)
            consecutive_failures = 0  # Reset on success
        
        except (requests.exceptions.RequestException, IOError) as e:
            logger.error("Error downloading %s: %s", img['url'], str(e))
            failed_downloads.append(img)
            consecutive_failures += 1
            
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                error_msg = f"Too many consecutive download failures ({consecutive_failures})"
                logger.critical(error_msg)
                raise SystemError(error_msg)
            continue

    if failed_downloads:
        logger.warning("Failed to download %d images", len(failed_downloads))


def notify_admin_of_failure(error_message: str, baseURL, recipient):
    """Send a private message to admin via Discourse API"""
   
    try:
        url = f"{baseURL}/posts.json"
        data = {
            'title': 'PhotoFrame Error Report',
            'raw': f"System encountered a critical error:\n\n```\n{error_message}\n```",
            'target_recipients': recipient,
            'archetype': 'private_message'
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info("Successfully sent error notification to admin")
    
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")


def main():
    try:
        logger.info("Starting photo frame image fetch")
        
        tagged_topics = get_tagged_topics(base_url, tag_name)
        if not tagged_topics:
            logger.info("No new topics since last fetch")
            return
            
        image_list = process_topics(tagged_topics)
        if not image_list:
            logger.info("No new images found in topics")
            return
            
        download_images(image_list)
        db.update_last_successful_fetch(datetime.now(timezone.utc))
        logger.info("Successfully completed photo frame image fetch")
        
    except SystemError as e:
        logger.critical("System error: %s", e)
        # notify_admin_of_failure(error_msg,base_url,discourse_admin)
        sys.exit(1)
        
    except requests.exceptions.RequestException as e:
        logger.error("API/Network error: %s", e)
        # notify_admin_of_failure(error_msg,base_url,discourse_admin)
        sys.exit(1)
        
    except Exception as e:
        logger.critical("Unexpected error: %s\n%s", e, traceback.format_exc())
        # notify_admin_of_failure(error_msg,base_url,discourse_admin)
        sys.exit(1)


if __name__ == "__main__":
    main()