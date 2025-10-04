FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src
COPY prisma ./prisma

# Generate Prisma client
RUN prisma generate

# Make setup script executable
COPY setup_db.py /app/setup_db.py
RUN chmod +x /app/setup_db.py

EXPOSE 8080

# Simple command to start the app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
