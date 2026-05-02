# Simple Dockerfile for development
FROM python:3.14-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python runtime deps listed in pyproject (installing explicitly)
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir google-genai pillow python-dotenv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY README.md ./

# Default command (can be overridden by docker-compose or at runtime)
CMD ["python", "src/main.py"]
