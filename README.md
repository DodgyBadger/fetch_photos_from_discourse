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

Copy the provided example configuration file and edit it with your settings:

```bash
cp .env-example .env
nano .env  # or use your preferred text editor
```

The `.env` file contains the following variables:

- `DISCOURSE_BASE_URL`: Your Discourse instance URL.
- `DISCOURSE_API_KEY`: API key generated in the Discourse admin panel.
- `DISCOURSE_API_USERNAME`: Username to use with the API.
- `DISCOURSE_TAG`: Fetch images contained within thopics with this tag.
- `FETCH_INTERVAL`: Time in minutes between image fetches (default: 60)
- `IMAGE_LIMIT`: Maximum number of images to be stored at any time. If exceeded, oldest images will be removed.
- `IMAGE_DIR`: Directory to store downloaded images. Only edit if you know what you are doing.

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
