# PhotoFrame

A digital photo frame application that displays images from Discourse.

## Project Structure

```
photoframe/
├── photoframe         # Main installation/management script
├── .env               # Main configuration file
├── requirements.txt   # Python dependencies
├── docker-compose.yml # Docker Compose configuration
├── config/            # Configuration directory
├── data/              # Application data
│   ├── images/        # Downloaded images
│   └── photoframe.db  # Application database
├── docker/            # Docker related files
│   ├── Dockerfile     # Container definition
│   └── entrypoint.sh  # Container startup script
├── logs/              # Log files
└── src/               # Python source code
```

## New Installation Method (Docker)

The new installation method uses Docker to isolate Python dependencies while keeping the display manager (Feh) on the host system.

### Prerequisites

- Docker
- Docker Compose (optional)
- Feh image viewer (installed automatically)
- Linux system with X11 or Wayland

### Quick Install

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/photoframe.git
   cd photoframe
   ```

2. Make the installation script executable:
   ```
   chmod +x photoframe
   ```

3. Run the installation with sudo:
   ```
   sudo ./photoframe install
   ```

### Commands

All commands should be run with sudo to ensure proper permissions:

- `sudo ./photoframe install` - Install and start PhotoFrame
- `sudo ./photoframe start` - Start services
- `sudo ./photoframe stop` - Stop services
- `sudo ./photoframe update` - Update to latest version
- `sudo ./photoframe status` - Check status

### Configuration

All configuration and data are now self-contained within the PhotoFrame directory:

- Configuration: `./config/`
- Data:
  - Images: `./data/images/`
  - Database: `./data/photoframe.db`
- Logs: `./logs/`

The main configuration file is at `./config/.env`, but you can also edit `.env` in the root directory. When installing, any existing `.env` file in the root will be used.

#### Custom Default Image

You can provide your own default image (logo, welcome screen, etc.):
1. Add a file named `default.jpg` or `default.png` to the PhotoFrame directory
2. Run the installation script

The default image will be displayed when Feh starts up, even if no other images have been downloaded yet. This ensures your display always shows something meaningful instead of an error.

## Alternative Installation Methods

### Manual Install (Development)

For development or testing without Docker:

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application:
   ```
   cp .env-example .env
   # Edit .env file with your settings
   ```

4. Run the application:
   ```
   python photoframe.py
   ```

### Docker Compose

You can also use Docker Compose directly:

1. Configure the application:
   ```
   cp .env-example .env
   # Edit .env file with your settings
   ```

2. Build and start the container:
   ```
   docker-compose up -d
   ```

3. Install and start Feh (host side):
   ```
   sudo apt-get install feh  # or your package manager
   feh --recursive --full-screen --slideshow-delay 30 ./images
   ```

## Troubleshooting

- **Feh not displaying images**: Check if your display environment is correctly detected. Edit the systemd service file or configure DISPLAY_SERVER in your .env file.

- **Container not starting**: Check the logs with `docker logs photoframe` or `sudo ./photoframe status`.

- **Missing images**: Ensure the `./images` directory exists and has appropriate permissions. If you encounter permission errors during installation, make sure you're running the commands with sudo.

- **Permission denied errors**: Make sure you're running all commands with sudo (e.g., `sudo ./photoframe install`). The installation script needs to create directories and install system services.

- **Display environment errors**: If you see errors like `feh ERROR: Can't open X display`, make sure you have a physical display connected or set up a virtual framebuffer (Xvfb).

- **No images displayed**: During installation, a default image is used to ensure Feh can start properly. If you only see this default image and no actual photos, check the logs to verify if image downloading is working correctly: `sudo ./photoframe status`. You can customize this default image by adding a file named `default.jpg` or `default.png` to your PhotoFrame directory before installation.