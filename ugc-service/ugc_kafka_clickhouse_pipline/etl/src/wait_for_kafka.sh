#!/usr/bin/env bash

# Function to wait for Kafka to be ready
wait_for_kafka() {
  echo "Waiting for Kafka to be ready..."

  until nc -z -w1 kafka1 9092; do
    echo "Kafka is unavailable - sleeping"
    sleep 10
  done

  echo "Kafka is up - executing command"
}

# Wait for Kafka cluster
wait_for_kafka

# Execute the main Python script
python main.py
