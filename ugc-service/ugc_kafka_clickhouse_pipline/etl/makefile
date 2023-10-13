PROJECT_NAME = CINEMA_CLICKHOUSE

all:
	@echo "make start - Запуск контейнеров."
	@echo "make stop - Выключение контейнеров."

start:
	docker-compose -f docker-compose-dev.yml up -d --build

stop:
	docker-compose -f docker-compose-dev.yml down
