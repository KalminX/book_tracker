# Use official Python runtime as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies for Pillow (image processing)
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the app code
COPY . /app/

# Expose the port Flask runs on (default 5000)
EXPOSE 5000

# Set environment variable for Flask app entry point
ENV FLASK_APP=app.py

# For production, run your app with gunicorn
# You can customize number of workers (e.g., 3) as needed
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
