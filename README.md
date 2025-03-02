# Photoframe

A Python application that fetches images from specifically tagged topics on a Discourse instance.

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

## Quick Installation

If you don't need to make any customizations to the code, you can install directly:

```bash
# Clone the repository
git clone https://github.com/DodgyBadger/fetch_photos_from_discourse.git
cd fetch_photos_from_discourse

# Make the photoframe script executable
chmod +x photoframe

# Run the installation
./photoframe install
```

For a more flexible setup that allows easier updates, see the "Installation & Updates" section below.

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
- `DISCOURSE_TAG`: Fetch images contained within topics with this tag.
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

## Installation & Updates

### First-time Installation

It's recommended to fork this repository on GitHub first, then clone your fork:

```bash
# Clone your forked repository
git clone https://github.com/YOUR-USERNAME/fetch_photos_from_discourse.git
cd fetch_photos_from_discourse

# Make the photoframe script executable
chmod +x photoframe

# Run the installation
./photoframe install
```

### Updating

To update to the latest version:

```bash
# Add the original repository as a remote (first time only)
git remote add upstream https://github.com/DodgyBadger/fetch_photos_from_discourse.git

# Fetch and merge updates from the original repository
git fetch upstream
git merge upstream/main

# Run the installation again to update dependencies
./photoframe install
```

This approach allows you to keep your local configuration while still getting updates from the original repository.

## Logs

Logs are stored in the `logs` directory. View recent logs with:

```bash
./photoframe status
```
