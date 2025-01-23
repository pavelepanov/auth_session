BACKEND_NAME=backend

# Файлы окружения
ENV_DEV=.env

DC=docker-compose
COMPOSE_FILE=docker-compose.yml

# Команды Docker Compose
DC=docker-compose
COMPOSE_FILE=docker-compose.yml

.PHONY: help
help:
	@echo "Используйте следующие команды:"
	@echo "  make up-dev        - Запуск проекта в режиме разработки (использует $(ENV_DEV))"

# Запуск проекта в режиме разработки
.PHONY: up-dev
up-dev: ENV_FILE=$(ENV_DEV)
up-dev:
	@$(DC) --env-file $(ENV_FILE) -f $(COMPOSE_FILE) up -d

# Остановка и удаление всех контейнеров
.PHONY: down
down:
	@$(DC) down

# Запуск миграций базы данных
.PHONY: migrate
migrate:
	@$(DC) exec $(BACKEND_NAME) alembic upgrade head

.PHONY: restart
restart:
	@$(DC) down
	@$(DC) --env-file $(ENV_DEV) -f $(COMPOSE_FILE) up -d
