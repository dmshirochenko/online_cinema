# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /data_generator

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    curl

# Install Python dependencies
COPY requirements.txt /data_generator
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /data_generator/

CMD ["python", "src/main.py"]
