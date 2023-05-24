FROM python:3.9-slim

RUN apt-get update && apt-get install -y fping systemctl cron

# Copy the application code
COPY ./app /app

# Install requirements 
RUN pip install -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# start App and cron
CMD ["/bin/bash", "-c", "systemctl enable cron --now && python3 wol.py"]