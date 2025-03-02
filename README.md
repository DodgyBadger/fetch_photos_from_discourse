# Photoframe

A Python application that fetches and manages images from Discourse for a digital photo frame display.

## Prerequisites

- **Python 3.8+** - Required to run the application
- **Package Manager** - One of the following:
  - **apt** - For Debian/Ubuntu-based systems
  - **Homebrew** - For macOS or Linux systems with Homebrew installed
- **Scheduler** - The script will automatically use one of:
  - **cron** - Traditional Unix/Linux scheduler
  - **systemd** - Modern Linux systems (Ubuntu 16.04+, Fedora, CentOS 7+, etc.)
  - **launchd** - macOS scheduler

### Compatible Operating Systems

- **Linux** - Debian/Ubuntu, Fedora, CentOS, Arch Linux, etc.
- **macOS** - 10.15 (Catalina) or newer
- **Raspberry Pi OS** - Bullseye or newer

## Installation

```bash
# Clone the repository
git clone https://github.com/DodgyBadger/fetch_photos_from_discourse.git
cd fetch_photos_from_discourse

# Make the photoframe script executable
chmod +x photoframe

# Run the installation
./photoframe install
```

## Configuration

Create a `.env` file in the project root with the following variables:

```
DISCOURSE_API_KEY=your_api_key
DISCOURSE_API_USERNAME=your_username
DISCOURSE_BASE_URL=https://your-discourse-instance.com
DISCOURSE_TAG=photo
BATCH_SIZE=20
IMAGE_LIMIT=1000
IMAGE_DIR=data/images
FETCH_INTERVAL=60
```

- `FETCH_INTERVAL`: Time in minutes between image fetches (default: 60)
- `IMAGE_LIMIT`: Maximum number of images to store (oldest will be removed)

## Commands

The `photoframe` script provides several commands:

- **install**: Set up the virtual environment, install dependencies, and configure the scheduler
- **run**: Run the image fetching process once manually
- **status**: Display current schedule, recent logs, and available commands
- **reschedule**: Change how often images are fetched
- **uninstall**: Remove the scheduler job and optionally the virtual environment

## Updating

To update to the latest version:

```bash
# Pull the latest changes
git pull

# Run the installation again to update dependencies
./photoframe install
```

## Logs

Logs are stored in the `logs` directory. View recent logs with:

```bash
./photoframe status
```
