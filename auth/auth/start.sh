#!/usr/bin/env bash

# Wait for Postgres
while ! nc -z $POSTGRES_AUTH_HOST $POSTGRES_AUTH_PORT; do
  echo "Waiting for postgres at $POSTGRES_AUTH_HOST:$POSTGRES_AUTH_PORT..."
  sleep 1
done

# Wait for Redis
# while ! nc -z $REDIS_HOST $REDIS_PORT; do
#   echo "Waiting for redis..."
#   sleep 1
# done

# Run migrations
alembic upgrade head
echo "Alembic updated"

cd src && python main.py
