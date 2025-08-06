FROM python:3.13-slim

RUN apt-get update && apt-get install -y fping systemctl cron netcat-traditional arp-scan

# Define Default ENV Variables
ENV PORT=5000 \
    IP=0.0.0.0

# Copy the application code
COPY ./app /app

# Install requirements 
RUN pip install -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Copy entrypoint
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# start App
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
