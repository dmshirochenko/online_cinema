#!/usr/bin/env bash

# Function to wait for Kafka to be ready
wait_for_kafka() {
  echo "Waiting for Kafka to be ready..."

  until nc -z -w1 kafka1 19092; do
    echo "Kafka is unavailable - sleeping"
    sleep 10
  done

  echo "Kafka is up - executing command"
}

# Wait for Kafka cluster
wait_for_kafka

# Start the application
cd src && gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
