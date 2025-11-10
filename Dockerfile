FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# System packages (curl for healthchecks/logs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY service ./service

WORKDIR /app/service

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["gunicorn", "service.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]


