FROM python:3.14.9-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /bin/uv

WORKDIR /auth

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --no-install-project

COPY src ./src
COPY LICENSE ./LICENSE
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-default-groups --no-editable

FROM python:3.14.9-slim-bookworm AS runtime

ENV PATH="/auth/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /auth
RUN groupadd --gid 10001 auth \
    && useradd --uid 10001 --gid auth --no-create-home --shell /usr/sbin/nologin auth

COPY --from=builder /auth/.venv /auth/.venv
COPY --from=builder /auth/src/auth/infrastructure/persistence_sqla/alembic ./src/auth/infrastructure/persistence_sqla/alembic
COPY alembic.ini ./alembic.ini

USER 10001:10001
EXPOSE 8000

CMD ["granian", "--interface", "asgi", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--workers-kill-timeout", "30", "--respawn-failed-workers", "--no-access-log", "auth.run:make_app"]
