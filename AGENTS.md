# Project guide for coding agents

## What this repository is

This is a Python 3.14 authentication service built with FastAPI. It implements
server-side web sessions, signup/login/logout, and role-based access for `user`
and `admin`. PostgreSQL stores users and sessions.

The application follows Clean Architecture. Keep dependencies pointing inward:

```text
HTTP / infrastructure -> application -> domain
          entrypoint wires implementations to interfaces
```

- `domain/`: persistence-free entities, value types, roles, and domain errors.
- `application/`: use-case interactors, ports in `interfaces/`, validators, and
  application errors. It may depend on `domain`, never on FastAPI, Dishka,
  SQLAlchemy, or concrete adapters.
- `infrastructure/`: implementations of application ports and imperative
  SQLAlchemy mappings.
- `presentation/`: FastAPI routes, cookie request adapter, ASGI middleware, and
  HTTP error translation. Routes should only translate input/output and invoke
  an interactor.
- `entrypoint/`: environment configuration, Dishka providers, and application
  composition. `auth.run:make_app()` is the application factory.

## Find code efficiently

This repository uses a local CodeGraph index. Before broad `grep`/`find` calls
or opening many files, use your agent's CodeGraph MCP integration when it is
configured. The agent-independent shell interface is always:

```bash
codegraph explore "<symbol or question>"
codegraph status
```

The index lives in `.codegraph/`, is machine-local, and is ignored by Git. No
agent-specific configuration is committed to this repository. If the index is
absent, install the CLI with `npm install -g @colbymchenry/codegraph` and run
`codegraph init`. Developers may connect that CLI to Codex, Claude Code, Gemini,
Cursor, or another MCP client using the client's own local configuration. If
CodeGraph is unavailable, fall back to `rg` and targeted file reads.

When available, use Context7 when implementation depends on current behavior
of FastAPI, Dishka, SQLAlchemy, Alembic, or another external library.

## Local setup and common commands

Dependencies and the lock file are managed with `uv`:

```bash
uv sync --all-groups
cp .env.example .env                 # fill every value
make infra-up                        # PostgreSQL
make migrate                         # alembic upgrade head
make app                             # reload-enabled Gunicorn on localhost
```

For the complete containerized stack, copy `.env.docker.example` to
`.env.docker`, fill it, then run `make up`. Useful commands are documented by
`make help`.

Local application and migration targets load `.env` with `uv run --env-file`;
override the path with `ENV_FILE`. Application configuration reads only the
process environment and must not import or call python-dotenv.
Keep configuration in `entrypoint/config.py` as plain dataclasses with
`from_env()` methods. Configuration types should depend only on the standard
library.

Required settings are PostgreSQL host/port/database/user/password,
`BACKEND_PORT`, `SESSION_EXPIRATION_MINUTES`, and `SESSION_TOKEN_HASH_SECRET`.
Never commit `.env` or `.env.docker`.

## Rules for changes

- Preserve the layer boundaries above. Domain entities must stay independent
  of frameworks and persistence.
- A new use case normally consists of request/response dataclasses and an
  interactor in `application/interactors/`. Add an application interface when
  the use case needs I/O, implement it under `infrastructure/adapters/`, bind it
  in `entrypoint/ioc/`, then expose it through a thin presentation route.
- Interactors own business decisions and transaction boundaries. Persist
  through gateways and commit business changes only after the use case succeeds.
  `IdentityProvider.get_current_user()` must run FIRST, before business changes:
  it may commit session renewal or removal on the same database session. This
  session maintenance shares the transaction with the interactor.
- SQLAlchemy uses imperative mappings of the anemic domain dataclasses. Adapter
  queries must use these domain entities and their mapped attributes, never
  import or query `Table` objects from `persistence_sqla/mappings/`. Keep direct
  table access in persistence mappings, migrations, and schema tooling.
  Domain dataclasses must remain free of SQLAlchemy imports and declarations.
  Schema changes must keep the domain
  entity, `infrastructure/persistence_sqla/mappings/`, and an Alembic migration
  consistent. Create migrations with
  `make migrate-create NAME='0002_short_description'`, choosing the next numeric
  filename prefix, and review generated SQL. Keep Alembic revision identifiers
  and `down_revision` links independent of the numbered filenames.
  Store Python enum values as strings with `native_enum=False`, without native
  PostgreSQL enum types. Session timestamps use `DateTime(timezone=True)` and
  timezone-aware UTC datetimes in application code.
- Register new interactors/adapters in the appropriate Dishka provider. Use
  request scope for request state and database sessions; use app scope for
  shared configuration, engines, and sessionmakers.
- Raise typed domain/application errors from inner layers. Map new HTTP-facing
  errors centrally in `presentation/http/base/error_handler.py`; do not build
  error responses inside interactors.
- A random bearer token is stored in the `__Host-session` HTTP-only cookie;
  PostgreSQL stores only its HMAC-SHA256 hash plus an independent UUID. Multiple
  sessions per user are allowed. Interactors communicate cookie changes through
  `ClientSessionTransport`; ASGI middleware emits the final cookie action.
  Set cookies only after successful commit. Preserve Secure and SameSite.
  For local HTTP set SESSION_COOKIE_NAME=session and SESSION_COOKIE_SECURE=false.
- Keep async I/O async. Do not place blocking database, broker, or password
  operations directly in route handlers.
- Follow the existing typed style, 88-character line length, and Ruff import
  ordering. Avoid unrelated formatting or refactors.

## Verification

Run the smallest relevant tests while iterating, then the full checks before
finishing:

```bash
uv run pytest tests/unit/application/interactors/test_log_in.py
make test
uv run ruff check .
uv run ruff format --check .
```

Tests mirror the source tree. Unit tests should mock application interfaces and
cover success plus business-error paths. Add integration coverage when behavior
depends on real SQLAlchemy mappings, migrations, cookies, middleware, or broker
wiring.

Before handing off a change, confirm that migrations are intentional, no secret
or local environment file is tracked, the CodeGraph index is current, and the
working-tree diff contains only task-related changes.
