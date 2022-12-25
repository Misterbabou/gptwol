FROM python:3.9-slim

RUN apt-get update && apt-get install -y iputils-ping

# Copy the application code
COPY . /app
RUN pip install -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Set the entrypoint
ENTRYPOINT ["python", "wol.py"]
