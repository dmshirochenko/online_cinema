#!/usr/bin/env bash

# Wait for Redis
while ! nc -z $REDIS_HOST $REDIS_PORT; do
  echo "Waiting for redis..."
  sleep 1
done

cd src && gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 main:app
