FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for SQLite database
RUN mkdir -p /app/instance

# Expose port
EXPOSE $PORT

# Run the application
CMD gunicorn app_new:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
