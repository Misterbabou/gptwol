FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y fping systemctl cron netcat-traditional arp-scan unzip curl

# Define ARG
ARG BOOTSTRAP_VERSION=5.3.7 \
    FONTAWESOME_VERSION=7.0.0

# Define Default ENV Variables
ENV PORT=5000 \
    IP=0.0.0.0

# Copy the application code
COPY ./app /app

# Create Directories
RUN mkdir -p /app/templates/assets/bootstrap/css /app/templates/assets/bootstrap/js && \
    mkdir -p /app/templates/assets/fontawesome/css /app/templates/assets/fontawesome/webfonts

# Download Bootstrap
RUN curl -sSL "https://github.com/twbs/bootstrap/releases/download/v${BOOTSTRAP_VERSION}/bootstrap-${BOOTSTRAP_VERSION}-dist.zip" -o /tmp/bootstrap.zip && \
    unzip /tmp/bootstrap.zip bootstrap-${BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css bootstrap-${BOOTSTRAP_VERSION}-dist/js/bootstrap.bundle.min.js -d /tmp/bootstrap && \
    cp /tmp/bootstrap/bootstrap-${BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css /app/templates/assets/bootstrap/css/ && \
    cp /tmp/bootstrap/bootstrap-${BOOTSTRAP_VERSION}-dist/js/bootstrap.bundle.min.js /app/templates/assets/bootstrap/js/

# Download Fontawesome
RUN curl -sSL "https://use.fontawesome.com/releases/v${FONTAWESOME_VERSION}/fontawesome-free-${FONTAWESOME_VERSION}-web.zip" -o /tmp/fontawesome.zip && \
    unzip /tmp/fontawesome.zip fontawesome-free-${FONTAWESOME_VERSION}-web/css/brands.min.css fontawesome-free-${FONTAWESOME_VERSION}-web/css/fontawesome.min.css fontawesome-free-${FONTAWESOME_VERSION}-web/css/solid.min.css "fontawesome-free-${FONTAWESOME_VERSION}-web/webfonts/*" -d /tmp/fontawesome && \
    cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/css/brands.min.css /app/templates/assets/fontawesome/css/ && \
    cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/css/fontawesome.min.css /app/templates/assets/fontawesome/css/ && \
    cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/css/solid.min.css /app/templates/assets/fontawesome/css/ && \
    cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/webfonts/* /app/templates/assets/fontawesome/webfonts/

# Clean after download
RUN rm -rf /tmp/bootstrap /tmp/bootstrap.zip /tmp/fontawesome /tmp/fontawesome.zip && \
    apt-get purge -y curl unzip && \
    apt-get autoremove -y && \
    apt-get clean

# Install requirements 
RUN pip install -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Copy entrypoint
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# start App
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
