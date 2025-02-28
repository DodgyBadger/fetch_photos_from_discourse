FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY src/ /app/

# Ensure logs directory exists
RUN mkdir -p /app/logs

# Set up cron for the photo fetch job (configuration happens at runtime)
RUN apt-get update && apt-get install -y cron && apt-get clean

# Copy entrypoint script - this will be created dynamically by the installation script
COPY docker/entrypoint.sh /app/entrypoint.sh

# Create necessary volumes
VOLUME ["/app/logs", "/data"]

# Set environment variables
ENV IMAGE_DIR=/data/images
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]