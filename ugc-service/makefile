PROJECT_NAME = CINEMA_NOTIFICATION

all:
	@echo "make start - Запуск контейнеров."
	@echo "make stop - Выключение контейнеров."

start:
	docker-compose -f docker-compose.yml up -d --build

stop:
	docker-compose -f docker-compose.yml down
