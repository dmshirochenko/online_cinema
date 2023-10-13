# Function to wait for Kafka to be ready
wait_for_kafka() {
  echo "Waiting for Kafka to be ready..."

  until nc -z -w1 kafka1 19092; do
    echo "Kafka is unavailable - sleeping"
    sleep 10
  done

  echo "Kafka is up - executing command"
}

wait_for_api() {
  echo "Waiting for event API to be ready..."
  until nc -z -w1 events_api 8000; do
    echo "Event API is unavailable - sleeping"
    sleep 10
  done

  echo "Event API is up - executing command"
}

# Wait for Kafka cluster
wait_for_kafka
wait_for_api
