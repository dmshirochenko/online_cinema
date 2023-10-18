#!/bin/sh
python3 /opt/app/tests/functional/utils/wait_for_es.py
python3 /opt/app/tests/functional/utils/wait_for_redis.py
export PYTHONPATH=$PYTHONPATH:/opt/app
pytest /opt/app/tests/functional -W ignore::DeprecationWarning
