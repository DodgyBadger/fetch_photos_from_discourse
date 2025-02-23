
import sqlite3
from datetime import datetime, timezone
from typing import Optional
import logging
from pathlib import Path


logger = logging.getLogger(__name__)

# Set the DB location
BASE_DIR = Path(__file__).parent
db_path = BASE_DIR / 'photoframe.db'

def init_db():
    """Initialize the SQLite database with our schema"""

    try:
        logger.info("Initializing database at %s", db_path)
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
        logger.info("Database initialization successful")
    except sqlite3.Error as e:
        logger.error("Database initialization failed: %s", e)
        raise
    finally:
        conn.close()


def get_image_count() -> int:
    """Get current number of images in database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        count = c.execute('SELECT COUNT(*) FROM images').fetchone()[0]
        return count
    except sqlite3.Error as e:
        logger.error("Failed to get image count: %s", e)
        raise
    finally:
        conn.close()


def is_image_downloaded(hash: str) -> bool:
    """Check if image hash already exists in database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        result = c.execute('SELECT 1 FROM images WHERE hash = ?', (hash,)).fetchone()
        return bool(result)
    except sqlite3.Error as e:
        logger.error("Failed to check image hash %s: %s", hash, e)
        raise
    finally:
        conn.close()


def remove_oldest_images(count: int):
    """Remove the specified number of oldest images"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Get files to delete
        files_to_delete = c.execute('''
            SELECT filename FROM images 
            ORDER BY downloaded_at ASC 
            LIMIT ?
        ''', (count,)).fetchall()
        
        logger.info("Removing %d oldest images", count)
        
        # Delete files from filesystem
        for (filename,) in files_to_delete:
            try:
                file_path = os.path.join(os.getenv('IMAGE_DIR'), filename)
                os.remove(file_path)
                logger.debug("Removed file: %s", file_path)
            except OSError as e:
                logger.error("Failed to remove file %s: %s", filename, e)
                raise
        
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
        logger.info("Successfully removed %d images", count)
    except sqlite3.Error as e:
        logger.error("Database error while removing old images: %s", e)
        raise
    finally:
        conn.close()


def add_image(hash: str, filename: str, url: str, downloaded_at: datetime):
    """Add a new image to the database"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO images (hash, filename, url, downloaded_at)
            VALUES (?, ?, ?, ?)
        ''', (hash, filename, url, downloaded_at))
        conn.commit()
        logger.debug("Added image to database: %s", filename)
    except sqlite3.Error as e:
        logger.error("Failed to add image %s to database: %s", filename, e)
        raise
    finally:
        conn.close()


def update_last_successful_fetch(timestamp: datetime):
    """Update the last successful fetch timestamp"""
    try:
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
        logger.debug("Updated last successful fetch to %s", timestamp.isoformat())
    except sqlite3.Error as e:
        logger.error("Failed to update last successful fetch: %s", e)
        raise
    finally:
        conn.close()


def get_last_successful_fetch() -> Optional[datetime]:
    """Get the timestamp of the last successful fetch"""
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        result = c.execute('''
            SELECT value FROM status 
            WHERE key = 'last_successful_fetch'
        ''').fetchone()
        
        if result:
            # Parse and ensure UTC
            dt = datetime.fromisoformat(result[0])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        return None
    except sqlite3.Error as e:
        logger.error("Failed to get last successful fetch: %s", e)
        raise
    finally:
        conn.close()