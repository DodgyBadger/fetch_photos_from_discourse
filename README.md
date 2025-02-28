# PhotoFrame

A digital photo frame application that displays images from Discourse.

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
   chmod +x photoframe-install
   ```

3. Run the installation:
   ```
   ./photoframe-install install
   ```

### Commands

- `./photoframe-install install` - Install and start PhotoFrame
- `./photoframe-install start` - Start services
- `./photoframe-install stop` - Stop services
- `./photoframe-install update` - Update to latest version
- `./photoframe-install status` - Check status

### Configuration

Configuration is stored in `~/.config/photoframe/.env`. You can edit this file to change settings.

Images are stored in `./images` relative to where you installed PhotoFrame. This directory is automatically created during installation.

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

- **Container not starting**: Check the logs with `docker logs photoframe` or `./photoframe-install status`.

- **Missing images**: Ensure the `./images` directory exists and has appropriate permissions.