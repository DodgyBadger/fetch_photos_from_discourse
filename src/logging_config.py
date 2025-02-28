import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging once for the entire application"""
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Set up file handler with rotation
    log_file = log_dir / 'photoframe.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,
        backupCount=5
    )
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    root_logger.handlers = []
    
    # Add both handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


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
