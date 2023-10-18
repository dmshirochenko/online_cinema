#!/bin/sh

set -e

docker-compose up -d --build --renew-anon-volumes
docker logs -f content_api_tests
exitcode="$(docker inspect content_api_tests --format={{.State.ExitCode}})"
docker-compose down --remove-orphans --volumes
exit "$exitcode"