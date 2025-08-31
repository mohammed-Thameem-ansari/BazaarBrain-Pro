# Backend Dockerfile for BazaarBrain-Pro
# Build:   docker build -t bazaarbrain-backend -f deploy/Dockerfile .
# Run:     docker run -p 8000:8000 --env-file .env.production bazaarbrain-backend

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional: add build tools if needed for psycopg2-binary or others)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy entire repo to ensure access to packages like `backend` and `agents`
COPY . /app

# Expose port
EXPOSE 8000

# Default command: run as package module to support relative imports
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
