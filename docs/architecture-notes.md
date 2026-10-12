# Заметки по архитектуре проекта

## Слои и ключевые файлы

| Часть | Где искать | Что делает |
|---|---|---|
| Domain: сущность пользователя | `src/auth/domain/entities/user.py` | Описывает `User` и создание пользователя без привязки к HTTP или базе данных. |
| Application: регистрация | `src/auth/application/interactors/sign_up.py` | `SignUpInteractor` выполняет сценарий регистрации: проверяет пользователя и пароль, создаёт пользователя, инициирует письмо и фиксирует транзакцию. |
| Application: интерфейс доступа к пользователям | `src/auth/application/interfaces/user_data_gateway.py` | `UserDataGateway` описывает операции, нужные сценарию: добавить пользователя, найти его и получить роль. Это контракт, а не SQL-код. |
| Infrastructure: реализация доступа к пользователям | `src/auth/infrastructure/adapters/user_data_mapper_sqla.py` | `UserDataMapperSqla` выполняет операции контракта с помощью SQLAlchemy и `AsyncSession`. |
| Infrastructure: отображение модели на таблицу | `src/auth/infrastructure/persistence_sqla/mappings/user.py` | Связывает доменный класс `User` с SQLAlchemy-таблицей `users`. Это не реализация `UserDataGateway`. |
| Presentation: HTTP handler регистрации | `src/auth/presentation/http/auth/sign_up.py` | Принимает `POST /auth/signup` и передаёт данные в `SignUpInteractor`. |
| Тесты | `tests/`, в частности `tests/unit/application/interactors/test_sign_up.py` | Проверяют сценарии отдельно от реальной базы, используя моки зависимостей. Общие fixtures находятся в `tests/conftest.py`. |

## Поток регистрации

```text
HTTP POST /auth/signup
  → presentation: sign_up handler
  → Dishka передаёт SignUpInteractor и его зависимости
  → application: SignUpInteractor выполняет сценарий
  → интерфейс UserDataGateway
  → infrastructure: UserDataMapperSqla + SQLAlchemy AsyncSession
  → PostgreSQL
```

Application зависит от интерфейса `UserDataGateway`, а не от SQLAlchemy-класса. Инфраструктурная реализация удовлетворяет этому интерфейсу. Поэтому сценарий регистрации не должен знать, каким способом gateway хранит данные.

Поток не означает, что запрос обязательно вызывает каждый слой ровно один раз. Например, сценарий также обращается к интерфейсам хешера паролей, генератора ID, отправителя писем и менеджера транзакций; Dishka предоставляет соответствующие реализации.

## Как зависимости собирает Dishka

Dependency Injection (внедрение зависимостей) означает, что объект получает нужные ему объекты извне, вместо того чтобы создавать их внутри себя.

В этом проекте:

1. `src/auth/entrypoint/ioc/interactors.py` регистрирует `SignUpInteractor` в `InteractorProvider`.
2. `src/auth/entrypoint/ioc/adapters.py` задаёт реализации интерфейсов. Например, `UserDataGateway` связывается с `UserDataMapperSqla`, а `PasswordHasher` — с `PasswordHasherBcrypt`. Там же создаются SQLAlchemy engine, фабрика сессий и сессии запросов.
3. `src/auth/entrypoint/ioc/registry.py` собирает providers.
4. `src/auth/entrypoint/setup.py` создаёт Dishka-контейнер из providers и конфигурации.
5. В handler `sign_up.py` аннотация `FromDishka[SignUpInteractor]` вместе с `@inject` просит Dishka передать готовый interactor.

Dishka читает типы параметров конструкторов и providers, строит цепочку объектов и создаёт её с нужными сроками жизни. Например:

```text
Config → AsyncEngine → sessionmaker → AsyncSession
                                  → UserDataMapperSqla
UserDataMapperSqla (как UserDataGateway) + остальные зависимости
                                  → SignUpInteractor
```

## Миграции базы данных

- `alembic.ini` указывает каталог миграций: `src/auth/infrastructure/persistence_sqla/alembic`.
- В `src/auth/infrastructure/persistence_sqla/alembic/env.py` Alembic получает URL базы из настроек приложения и настраивает запуск миграций.
- Файлы в `src/auth/infrastructure/persistence_sqla/alembic/versions/` содержат последовательные изменения схемы.
- `alembic upgrade head` применяет все ещё не применённые миграции до последней.
- В `Makefile` цель `docker-migrate` запускает эту команду во временном контейнере сервиса `backend` и удаляет контейнер после завершения. Изменения схемы остаются в PostgreSQL.

Команда из корня проекта в среде, где установлен `make`:

```sh
make docker-migrate
```

Эквивалентная команда Docker Compose для PowerShell:

```powershell
docker compose --env-file .env.docker -f docker-compose.yml run --rm backend alembic upgrade head
```

Здесь `backend` — имя сервиса из `docker-compose.yml`, а `--rm` удаляет одноразовый контейнер после выполнения команды.

## Запуск тестов

В `Makefile` тесты запускаются так:

```sh
uv run pytest tests/ --cov=auth --cov-report=term-missing -n auto
```

Команда запускает pytest для каталога `tests/`, считает покрытие пакета `auth` и распределяет тесты между процессами. Для одного тестового файла можно использовать, например:

```sh
uv run pytest tests/unit/application/interactors/test_sign_up.py
```

Тесты `SignUpInteractor` подменяют gateway, хешер и другие зависимости моками. Так проверяется логика сценария без подключения к PostgreSQL или RabbitMQ.
