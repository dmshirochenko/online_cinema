#!/usr/bin/env bash

# Wait for Postgres
#while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
#  echo "Waiting for postgres..."
#  sleep 1
#done

# SQLite -> Postgres
python src/load_sqlite.py

# Wait for Elastic
while ! nc -z $ES_HOST $ES_PORT; do
  echo "Wating for elastic..."
  sleep 1
done

# Postgres -> Elastic
python src/main.py
