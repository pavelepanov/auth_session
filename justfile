set positional-arguments

env_file := env("ENV_FILE", ".env")
docker_env_file := env("ENV_DOCKER_FILE", ".env.docker")

[private]
default:
    @just --list

# Поднять PostgreSQL, применить миграции, создать тестовых пользователей и запустить Granian.
dev:
    uv sync --locked
    docker compose --env-file "{{ env_file }}" -f compose.local.yaml up -d --wait
    uv run --locked --env-file "{{ env_file }}" alembic upgrade head
    uv run --locked --env-file "{{ env_file }}" python -m auth.infrastructure.persistence_sqla.seed_users
    uv run --locked --env-file "{{ env_file }}" sh -eu -c 'exec granian --interface asgi --factory --host 127.0.0.1 --port "$BACKEND_PORT" --workers 4 --no-access-log --reload --reload-paths src auth.run:make_app'

# Собрать и запустить полный стек, дождаться готовности.
up: (compose "docker" "up" "--build" "-d" "--wait" "--wait-timeout" "120")

# Остановить стек с сохранением данных: just down [docker|local].
down mode="docker": (compose mode "down")

# Применить миграции вручную: just migrate [local|docker].
migrate mode="local":
    #!/usr/bin/env sh
    set -eu
    case "$1" in
        local)
            exec uv run --locked --env-file "{{ env_file }}" alembic upgrade head
            ;;
        docker)
            exec docker compose --env-file "{{ docker_env_file }}" -f compose.yaml run --build --rm backend alembic upgrade head
            ;;
        *)
            echo 'Допустимые режимы: local, docker' >&2
            exit 2
            ;;
    esac

# Создать тестовых пользователей: just seed-users [local|docker].
seed-users mode="local":
    #!/usr/bin/env sh
    set -eu
    case "$1" in
        local)
            exec uv run --locked --env-file "{{ env_file }}" python -m auth.infrastructure.persistence_sqla.seed_users
            ;;
        docker)
            exec docker compose --env-file "{{ docker_env_file }}" -f compose.yaml exec -T backend python -m auth.infrastructure.persistence_sqla.seed_users
            ;;
        *)
            echo 'Допустимые режимы: local, docker' >&2
            exit 2
            ;;
    esac

# Любая команда Compose: just compose local logs -f / just compose docker ps.
compose mode +args:
    #!/usr/bin/env sh
    set -eu
    case "$1" in
        local)
            config_file=compose.local.yaml
            settings_file="{{ env_file }}"
            ;;
        docker)
            config_file=compose.yaml
            settings_file="{{ docker_env_file }}"
            ;;
        *)
            echo 'Допустимые режимы: local, docker' >&2
            exit 2
            ;;
    esac
    shift
    exec docker compose --env-file "$settings_file" -f "$config_file" "$@"

# Проверить стиль, форматирование и типы.
check:
    uv run --locked ruff check .
    uv run --locked ruff format --check .
    uv run --locked --all-groups mypy

# Все тесты параллельно с coverage; можно передать файл тестов и параметры pytest.
test *args:
    uv run --locked --group test python -m pytest -n auto --cov=auth --cov-branch --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90 "$@"

# Все тесты параллельно без coverage; можно передать файл тестов и параметры pytest.
test-no-cov *args:
    uv run --locked --group test python -m pytest -p no:pytest_cov -n auto "$@"
