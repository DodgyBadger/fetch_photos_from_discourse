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

# Copy application files
COPY . .

# Ensure logs directory exists
RUN mkdir -p /app/logs

# Set up cron job for photo frame checks
RUN echo "*/15 * * * * cd /app && python /app/photoframe.py >> /app/logs/photoframe.log 2>&1" > /etc/cron.d/photoframe && \
    chmod 0644 /etc/cron.d/photoframe

# Create an entrypoint script
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'cd /app' >> /entrypoint.sh && \
    echo 'python -c "from db import init_db; init_db()"' >> /entrypoint.sh && \
    echo 'cron' >> /entrypoint.sh && \
    echo 'echo "PhotoFrame started. Use docker logs to view output."' >> /entrypoint.sh && \
    echo 'tail -f /dev/null' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Create necessary volumes
VOLUME ["/app/logs", "/data"]

# Set environment variables
ENV IMAGE_DIR=/data/images
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/entrypoint.sh"]