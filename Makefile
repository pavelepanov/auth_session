# Конфигурация 
ENV_FILE=.env
ENV_DOCKER_FILE=.env.docker
DC=docker-compose
COMPOSE_FILE=docker-compose.yml

GUNICORN_CONF=conf/gunicorn.conf.py
APP_FACTORY=auth.run:make_app()

BACKEND_SERVICE=backend

# Help 
.PHONY: help
help:
	@echo ""
	@echo "  Инфраструктура (Docker):"
	@echo "    make infra-up          — Поднять инфраструктуру (PostgreSQL, RabbitMQ)"
	@echo "    make infra-down        — Остановить инфраструктуру"
	@echo ""
	@echo "  Приложение (локально):"
	@echo "    make app               — Запустить FastAPI через gunicorn"
	@echo ""
	@echo "  Миграции (локально):"
	@echo "    make migrate           — Применить миграции (alembic upgrade head)"
	@echo "    make migrate-down      — Откатить последнюю миграцию (alembic downgrade -1)"
	@echo "    make migrate-create    — Создать новую миграцию (NAME=описание)"
	@echo ""
	@echo "  Миграции (через контейнер):"
	@echo "    make docker-migrate    — Одноразовый контейнер: alembic upgrade head (стек не трогается)"
	@echo ""
	@echo "  Тесты:"
	@echo "    make test              — Запустить тесты с покрытием (-n auto)"
	@echo ""
	@echo "  Полный стек (Docker):"
	@echo "    make up                — Поднять всё (инфраструктура + backend)"
	@echo "    make down              — Остановить всё"
	@echo ""

# Инфраструктура

.PHONY: infra-up
infra-up:
	@$(DC) --env-file $(ENV_DOCKER_FILE) -f $(COMPOSE_FILE) up -d postgres rabbitmq

.PHONY: infra-down
infra-down:
	@$(DC) --env-file $(ENV_DOCKER_FILE) -f $(COMPOSE_FILE) down

# Приложение (локально через gunicorn)

.PHONY: app
app:
	uv run gunicorn -c $(GUNICORN_CONF) '$(APP_FACTORY)' --reload

# Миграции (локально)

.PHONY: migrate
migrate:
	uv run alembic upgrade head

.PHONY: migrate-down
migrate-down:
	uv run alembic downgrade -1

.PHONY: migrate-create
migrate-create:
	@if [ -z "$(NAME)" ]; then \
		echo "Ошибка: укажите NAME. Пример: make migrate-create NAME='add_users_table'"; \
		exit 1; \
	fi
	uv run alembic revision --autogenerate -m "$(NAME)"

# Миграции (через контейнер)
# Поднимает одноразовый контейнер backend,
# выполняет миграции, контейнер удаляется.
# Основной стек не затрагивается.

.PHONY: docker-migrate
docker-migrate:
	@echo ">>> Запускаем одноразовый контейнер для миграций..."
	@$(DC) --env-file $(ENV_DOCKER_FILE) -f $(COMPOSE_FILE) run --rm $(BACKEND_SERVICE) alembic upgrade head
	@echo ">>> Миграции применены. Контейнер удалён."

# Тесты

.PHONY: test
test:
	uv run pytest tests/ --cov=auth --cov-report=term-missing -n auto

# Полный стек (Docker)

.PHONY: up
up:
	@$(DC) --env-file $(ENV_DOCKER_FILE) -f $(COMPOSE_FILE) up -d

.PHONY: down
down:
	@$(DC) --env-file $(ENV_DOCKER_FILE) -f $(COMPOSE_FILE) down
