#!/bin/sh

set -e

docker-compose up -d --build --renew-anon-volumes
docker logs -f api_ugc_test
exitcode="$(docker inspect api_ugc_test --format={{.State.ExitCode}})"
docker-compose down --remove-orphans --volumes
exit "$exitcode"