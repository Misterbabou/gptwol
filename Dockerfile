# ---- Builder stage: install build deps, download assets, build wheels ----
FROM python:3.13-slim AS builder

ARG BOOTSTRAP_VERSION=5.3.8
ARG FONTAWESOME_VERSION=7.1.0

# install build deps + tools used to download/unzip
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libffi-dev python3-dev gcc pkg-config curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy app (so downloads land inside /app)
COPY ./app /app

# create asset dirs + download bootstrap & fontawesome into /app
RUN mkdir -p /app/templates/assets/bootstrap/css /app/templates/assets/bootstrap/js \
 && mkdir -p /app/templates/assets/fontawesome/css /app/templates/assets/fontawesome/webfonts \
 && curl -sSL "https://github.com/twbs/bootstrap/releases/download/v${BOOTSTRAP_VERSION}/bootstrap-${BOOTSTRAP_VERSION}-dist.zip" -o /tmp/bootstrap.zip \
 && unzip /tmp/bootstrap.zip bootstrap-${BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css bootstrap-${BOOTSTRAP_VERSION}-dist/js/bootstrap.bundle.min.js -d /tmp/bootstrap \
 && cp /tmp/bootstrap/bootstrap-${BOOTSTRAP_VERSION}-dist/css/bootstrap.min.css /app/templates/assets/bootstrap/css/ \
 && cp /tmp/bootstrap/bootstrap-${BOOTSTRAP_VERSION}-dist/js/bootstrap.bundle.min.js /app/templates/assets/bootstrap/js/ \
 && curl -sSL "https://use.fontawesome.com/releases/v${FONTAWESOME_VERSION}/fontawesome-free-${FONTAWESOME_VERSION}-web.zip" -o /tmp/fontawesome.zip \
 && unzip /tmp/fontawesome.zip fontawesome-free-${FONTAWESOME_VERSION}-web/css/brands.min.css fontawesome-free-${FONTAWESOME_VERSION}-web/css/fontawesome.min.css fontawesome-free-${FONTAWESOME_VERSION}-web/css/solid.min.css "fontawesome-free-${FONTAWESOME_VERSION}-web/webfonts/*" -d /tmp/fontawesome \
 && cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/css/brands.min.css /app/templates/assets/fontawesome/css/ \
 && cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/css/fontawesome.min.css /app/templates/assets/fontawesome/css/ \
 && cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/css/solid.min.css /app/templates/assets/fontawesome/css/ \
 && cp /tmp/fontawesome/fontawesome-free-${FONTAWESOME_VERSION}-web/webfonts/* /app/templates/assets/fontawesome/webfonts/ \
 && rm -rf /tmp/bootstrap /tmp/bootstrap.zip /tmp/fontawesome /tmp/fontawesome.zip

# Install Python deps into a relocatable prefix (/install)
RUN pip install --no-cache-dir --prefix=/install -r /app/requirements.txt \
 && rm -rf /root/.cache/pip

# ---- Final stage: runtime only (no build deps) ----
FROM python:3.13-slim

ARG BOOTSTRAP_VERSION=5.3.7
ARG FONTAWESOME_VERSION=7.0.0

# install only runtime packages (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
      fping cron netcat-traditional arp-scan \
    && rm -rf /var/lib/apt/lists/*

# copy the installed python packages + app assets from builder
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

# Default ENV
ENV PORT=5000 \
    IP=0.0.0.0

WORKDIR /app

# entrypoint
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
