# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for scientific stack and Postgres
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prisma CLI for client generation
RUN pip install --no-cache-dir prisma==0.15.0

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY prisma ./prisma

# Generate prisma client
RUN prisma generate

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8080

CMD ["/app/start.sh"]
