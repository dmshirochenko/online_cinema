#!/usr/bin/env bash

set -e

chown www-data:www-data /var/log

python manage.py collectstatic --noinput

if [ "${DJANG0_COLECT_MIGRATE}" -eq "1" ]; then
  echo "Django migration is up"
  python manage.py makemigrations
  python manage.py migrate
fi

uwsgi --strict --ini uwsgi.ini --listen 1024
