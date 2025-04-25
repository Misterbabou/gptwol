#!/bin/bash

echo "Launching GPTWOL..."

systemctl enable cron --now

# Launch application
cd /app
gunicorn --access-logfile - wol:app
