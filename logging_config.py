import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
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
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get the logger and set its level
    logger = logging.getLogger('photoframe')
    logger.setLevel(logging.INFO)
    
    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
