#!/bin/bash

# Start cron service
service cron start

# Log that cron was started
echo "Cron service started at $(date)" >> /var/log/cron.log

# Run the certificate updater once at startup to ensure we have current URLs
echo "Running initial certificate update..." >> /var/log/cron.log
/usr/local/bin/python3 /app/update_certificate_links.py >> /var/log/cron.log 2>&1

# Start the main application
exec /usr/local/bin/python3 /app/main.py