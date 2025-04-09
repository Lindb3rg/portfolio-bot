# Use Python 3.11 as the base image
FROM python:3.11-slim

# Install AWS CLI and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    unzip \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create volume mount points
VOLUME /app
VOLUME /app/config

# Copy the update certificates script and make it executable
COPY update_certificate_links.py /app/
RUN chmod +x /app/update_certificate_links.py

# Copy the rest of the application
COPY . .

# Set up cron job for certificate updating


RUN echo "*/5 * * * * /usr/local/bin/python /app/update_certificate_links.py >> /var/log/cron.log 2>&1" > /etc/cron.d/cert-updater
# RUN echo "0 1 * * 1 python /app/update_certificate_links.py >> /var/log/cron.log 2>&1" > /etc/cron.d/cert-updater
RUN chmod 0644 /etc/cron.d/cert-updater
RUN crontab /etc/cron.d/cert-updater

# Create log file
RUN touch /var/log/cron.log

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port Gradio will run on
EXPOSE 7860

# Use the entrypoint script to start both cron and the main application
ENTRYPOINT ["/entrypoint.sh"]