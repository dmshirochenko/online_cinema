# Use the official Python 3.10 image
FROM python:3.10

# Set the working directory
WORKDIR /opt/app

# Set environment variables for Python to prevent it from generating .pyc files and to force unbuffered mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install netcat-traditional utility and clean up
RUN apt-get update && apt-get install -y netcat-traditional && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Upgrade pip and install required Python packages
RUN pip install pip --upgrade --no-cache-dir \
    && pip install -r requirements.txt --no-cache-dir

# Copy the rest of the application code into the container
COPY . .

# Make the start script executable
RUN chmod +x /opt/app/start.sh
