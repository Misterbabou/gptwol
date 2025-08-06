#!/bin/bash

echo "Launching GPTWOL..."

systemctl enable cron --now

# Launch application
cd /app
GUNICORN_CMD_ARGS="--bind=$IP:$PORT" gunicorn --access-logfile - wol:app
