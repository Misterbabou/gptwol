#!/bin/bash

echo "Launching GPTWOL..."

#Launch Cron
cron

# Launch application
cd /app
GUNICORN_CMD_ARGS="--bind=$IP:$PORT" gunicorn --access-logfile - wol:app
