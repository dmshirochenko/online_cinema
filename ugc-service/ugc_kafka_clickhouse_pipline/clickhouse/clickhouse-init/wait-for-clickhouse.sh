#!/bin/bash

# Wait until ClickHouse is up and running
until nc -z -w1 clickhouse-node1 9000; do
    echo "Waiting for ClickHouse to start..."
    sleep 10
done

# Execute the provided command
exec "${@}"
