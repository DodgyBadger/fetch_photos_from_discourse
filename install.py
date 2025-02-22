import os
import sys
import subprocess
import shutil
from typing import Optional
from enum import Enum
from datetime import datetime
from crontab import CronTab
from dotenv import load_dotenv
from db import init_db
from logging_config import setup_logging

logger = setup_logging()

class DisplayServer(Enum):
    X11 = 'x11'
    WAYLAND = 'wayland'
    AUTO = 'auto'


class SystemConfig:
    """System configuration handler"""
    def __init__(self):
        self.image_dir = os.getenv('IMAGE_DIR')
        self.slideshow_delay = int(os.getenv('SLIDESHOW_DELAY', '30'))
        self.display_mode = os.getenv('DISPLAY_MODE', 'fullscreen')
        self.display_server = os.getenv('DISPLAY_SERVER', 'auto')
        self.package_manager = os.getenv('PACKAGE_MANAGER', 'apt')
        self.system_user = os.getenv('SYSTEM_USER', os.getenv('USER'))
        self.service_name = os.getenv('SERVICE_NAME', 'photoframe')
        self.feh_options = os.getenv('FEH_ADDITIONAL_OPTIONS', '')
        self.run_as_sudo = os.getenv('RUN_AS_SUDO', 'true').lower() == 'true'
        self.check_interval = int(os.getenv('FETCH_INTERVAL', '900'))


    def run_privileged(self, cmd: list) -> None:
        """Run a command with sudo if configured"""
        if self.run_as_sudo:
            subprocess.run(['sudo'] + cmd, check=True)
        else:
            subprocess.run(cmd, check=True)

    def get_feh_command(self) -> str:
        """Build Feh command based on configuration"""
        cmd = ['/usr/bin/feh', '--recursive']
        
        if self.display_mode == 'fullscreen':
            cmd.append('--full-screen')
            
        cmd.extend([
            f'--slideshow-delay', str(self.slideshow_delay),
            self.image_dir
        ])
        
        if self.feh_options:
            cmd.extend(self.feh_options.split())
            
        return ' '.join(cmd)

    def get_display_environment(self) -> str:
        """Get display server environment variables"""
        display_server = self.detect_display_server() if self.display_server == 'auto' else self.display_server
        
        if display_server == DisplayServer.WAYLAND.value:
            return """Environment=WAYLAND_DISPLAY=wayland-0
Environment=XDG_RUNTIME_DIR=/run/user/%U"""
        return "Environment=DISPLAY=:0"

    def detect_display_server(self) -> str:
        """Determine if system is running X11 or Wayland"""
        try:
            session_type = subprocess.check_output(
                ['loginctl', 'show-session', '$(loginctl | grep $(whoami) | awk \'{print $1}\')', '-p', 'Type'],
                shell=True,
                text=True
            ).strip()
            
            return DisplayServer.WAYLAND.value if 'wayland' in session_type.lower() else DisplayServer.X11.value
        except subprocess.CalledProcessError:
            logger.warning("Could not determine display server type, defaulting to X11")
            return DisplayServer.X11.value


def check_and_install_feh(config: SystemConfig):
    """Check if Feh is installed and install if needed"""
    try:
        if shutil.which('feh') is None:
            logger.info("Feh not found, attempting to install...")
            
            if config.package_manager == 'apt':
                config.run_privileged(['apt-get', 'update'])
                config.run_privileged(['apt-get', 'install', '-y', 'feh'])
            else:
                raise NotImplementedError(f"Package manager {config.package_manager} not supported")
            
            if shutil.which('feh') is None:
                raise RuntimeError("Feh installation failed")
                
            logger.info("Feh installed successfully")
        else:
            logger.info("Feh is already installed")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Feh: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while installing Feh: {str(e)}")
        raise


def setup_feh_service(config: SystemConfig):
    """Create and enable systemd service for Feh"""

    """Create and enable systemd service for Feh"""
    if not shutil.which('systemctl'):
        logger.info("systemctl not found - this is normal in development environments")
        logger.info("In production, this script will create and enable a systemd service for Feh")
        return

    service_content = f"""[Unit]
    Description=Feh Photo Frame Slideshow
    After=network.target graphical-session.target

    [Service]
    Type=simple
    User=%i
    {config.get_display_environment()}
    ExecStart={config.get_feh_command()}
    Restart=always
    RestartSec=3

    # Security measures
    NoNewPrivileges=yes
    ProtectSystem=strict
    ProtectHome=read-only
    PrivateTmp=yes

    [Install]
    WantedBy=graphical.target
    """
    try:
        service_path = f'/etc/systemd/system/{config.service_name}@.service'
        
        with open(f'/tmp/{config.service_name}@.service', 'w') as f:
            f.write(service_content)
        
        config.run_privileged(['mv', f'/tmp/{config.service_name}@.service', service_path])
        config.run_privileged(['systemctl', 'daemon-reload'])
        config.run_privileged(['systemctl', 'enable', f'{config.service_name}@{config.system_user}'])
        config.run_privileged(['systemctl', 'start', f'{config.service_name}@{config.system_user}'])
        
        logger.info("Feh service installed and started successfully")
        
    except Exception as e:
        logger.error(f"Failed to setup Feh service: {str(e)}")
        raise


def setup_cron_jobs(config: SystemConfig, install_path: str):
    """Setup cron jobs for PhotoFrame application"""

    if not shutil.which('crontab'):
        logger.info("crontab not found - this is normal in development environments")
        logger.info("In production, this script will create a cron job to check for new images every %d minutes", config.check_interval)
        return

    try:
        # Get current user's crontab
        cron = CronTab(user=True)  # or just CronTab()

        # Remove any existing photoframe jobs
        cron.remove_all(comment='photoframe')
        
        # Add main check job to fetch new images
        check_job = cron.new(
            command=f'/usr/bin/python3 {install_path}/photoframe.py',
            comment='photoframe'
        )
        check_job.minute.every(config.check_interval)
        
        cron.write()
        logger.info("Cron job successfully configured")
        
    except Exception as e:
        logger.error(f"Failed to setup cron job: {str(e)}")
        raise


def create_directories(config: SystemConfig):
    """Create necessary directories for PhotoFrame"""
    try:
        if not config.image_dir:
            raise ValueError("IMAGE_DIR not configured")
            
        os.makedirs(config.image_dir, exist_ok=True)
        logger.info(f"Successfully created/verified directory: {config.image_dir}")
        
    except ValueError as ve:
        logger.error(str(ve))
        raise
    except OSError as oe:
        logger.error(f"Failed to create directories: {str(oe)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating directories: {str(e)}")
        raise


def main():
    """Main setup function for PhotoFrame"""
    try:
        logger.info("Starting PhotoFrame setup")
        
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Initialize configuration
        config = SystemConfig()
        
        # Create directories
        logger.info("Creating required directories")
        create_directories(config)
        
        # Initialize database
        logger.info("Initializing database")
        init_db()
        
        # Check and install Feh
        logger.info("Checking Feh installation")
        check_and_install_feh(config)
        
        # Setup Feh service
        logger.info("Setting up Feh service")
        setup_feh_service(config)
        
        # Setup cron job
        logger.info("Setting up cron job")
        install_path = os.path.dirname(os.path.abspath(__file__))
        setup_cron_jobs(config, install_path)
        
        logger.info("PhotoFrame setup completed successfully")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()