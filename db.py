
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# Get the directory where install.py is located
BASE_DIR = Path(__file__).parent
db_path = BASE_DIR / 'photoframe.db'

def init_db():
    """Initialize the SQLite database with our schema"""
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Table to track downloaded images
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            hash TEXT UNIQUE,
            filename TEXT,
            url TEXT,
            downloaded_at TIMESTAMP
        )
    ''')

    # Logging table
    c.execute('''
        CREATE TABLE IF NOT EXISTS status (
            key TEXT PRIMARY KEY,
            value TIMESTAMP
        )
    ''')
    
    # Create index on hash for quick lookups
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_image_hash 
        ON images(hash)
    ''')
    
    conn.commit()
    conn.close()

def get_image_count() -> int:
    """Get current number of images in database"""
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    count = c.execute('SELECT COUNT(*) FROM images').fetchone()[0]
    conn.close()
    return count

def is_image_downloaded(hash: str) -> bool:
    """Check if image hash already exists in database"""

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    result = c.execute('SELECT 1 FROM images WHERE hash = ?', (hash,)).fetchone()
    conn.close()
    return bool(result)

def remove_oldest_images(count: int):
    """Remove the specified number of oldest images"""
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get files to delete
    files_to_delete = c.execute('''
        SELECT filename FROM images 
        ORDER BY downloaded_at ASC 
        LIMIT ?
    ''', (count,)).fetchall()
    
    # Delete files from filesystem
    for (filename,) in files_to_delete:
        try:
            os.remove(os.path.join(os.getenv('IMAGE_DIR'), filename))
        except OSError as e:
            print(f"Error removing file {filename}: {e}")
    
    # Remove from database
    c.execute('''
        DELETE FROM images 
        WHERE id IN (
            SELECT id FROM images 
            ORDER BY downloaded_at ASC 
            LIMIT ?
        )
    ''', (count,))
    
    conn.commit()
    conn.close()


def add_image(hash: str, filename: str, url: str, downloaded_at: datetime):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO images (hash, filename, url, downloaded_at)
        VALUES (?, ?, ?, ?)
    ''', (hash, filename, url, downloaded_at))
    conn.commit()
    conn.close()

def update_last_successful_fetch(timestamp: datetime):
    # Ensure timestamp is UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO status (key, value)
        VALUES ('last_successful_fetch', ?)
    ''', (timestamp.isoformat(),))
    conn.commit()
    conn.close()

def get_last_successful_fetch() -> Optional[datetime]:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    result = c.execute('''
        SELECT value FROM status 
        WHERE key = 'last_successful_fetch'
    ''').fetchone()
    conn.close()
    
    if result:
        # Parse and ensure UTC
        dt = datetime.fromisoformat(result[0])
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    return None