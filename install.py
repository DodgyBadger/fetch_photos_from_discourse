import os
from datetime import datetime
from crontab import CronTab
from dotenv import load_dotenv
import logfire
from db import init_db

logfire.configure()


def setup_cron_jobs(install_path):
    # Get current user's crontab
    cron = CronTab(user=True)
    
    # Clear any existing photoframe jobs
    cron.remove_all(comment='photoframe')
    
    # Add main check job (every 15 minutes)
    check_job = cron.new(
        command=f'/usr/bin/python3 {install_path}/check_images.py',
        comment='photoframe'
    )
    check_job.minute.every(15)
    
    # Add daily cleanup job (4 AM)
    cleanup_job = cron.new(
        command=f'/usr/bin/python3 {install_path}/cleanup.py',
        comment='photoframe'
    )
    cleanup_job.hour.on(4)
    cleanup_job.minute.on(0)
    
    # Add status post job (noon)
    status_job = cron.new(
        command=f'/usr/bin/python3 {install_path}/post_status.py',
        comment='photoframe'
    )
    status_job.hour.on(12)
    status_job.minute.on(0)
    
    # Write the crontab
    cron.write()


def create_directories():
    """Create necessary directories"""
    image_dir = os.getenv('IMAGE_DIR')
    os.makedirs(image_dir, exist_ok=True)


def main():
    load_dotenv()
    
    print("Setting up PhotoFrame...")
    
    # Create directories
    print("Creating directories...")
    create_directories()
    
    # Initialize database
    print("Initializing database...")
    init_db()
    
    # Setup cron jobs
    # print("Setting up cron jobs...")
    # install_path = os.path.dirname(os.path.abspath(__file__))
    # setup_cron_jobs(install_path)
    
    print("Installation complete!")


if __name__ == "__main__":
    main()