#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

while ! nc -z "${DB_HOST_NAME}" "${DB_PORT}"; do
      echo "Checking DB at ${DB_HOST}:${DB_PORT}"
      echo "Database is not up. Wait for short time"
      sleep 5
done

if [ "${DJANG0_COLECT_MIGRATE}" -eq "1" ]; then
  echo "Django migration and static file collections is up"
  python manage.py makemigrations
  python manage.py migrate
fi

uwsgi --strict --ini uwsgi.ini --listen 1024
