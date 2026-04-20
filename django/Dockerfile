FROM python:3.11

LABEL org.opencontainers.image.source="https://github.com/4rkad/labelbase-django"
LABEL org.opencontainers.image.description="Labelbase Django backend, 4rkad Umbrel fork"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app/

RUN apt-get update && \
    apt-get install -y \
        default-libmysqlclient-dev \
        build-essential \
        cron vim logrotate \
        libpcre2-dev \
        default-mysql-client \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Cleanup to reduce image size
RUN apt-get purge -y --auto-remove build-essential

# 4rkad fork: run as uid 1000 so bind-mounted volumes from Umbrel work
RUN chown -R 1000:1000 /app
USER 1000:1000
