# Важно⚠️
**Проект написан специально для моего [Ютуб канала | Паша в мире АйТи](https://www.youtube.com/@PashaVmireIT) \
Если ты не видел теорию, а также процесс написания данного проекта – быстрее беги [смотреть](https://www.youtube.com/@PashaVmireIT)**

# Введение
Проект, реализующий работу с:
1. Web sessions
2. RBAC

# Проект
## Технологический стек
- **Python**: `3.12`
- **Production**: `alembic`, `dishka`, `fastapi`, `psycopg`, `sqlalchemy[async]`, `gunicorn`, `faststream[rabbit]`
- **Development**: `isort`, `ruff`, `pre-commit`


## API
<p align="center">
  <img src="docs/API.png" />
  <br><em>Handlers</em>
</p>

### General
- '/': Открыт для **всех**
   - Перенаправляет на Swagger документацию

### Auth (`/auth`)

- 'signup' (POST): Открыт для **всех**
  - Регистрация аккаунта
- 'login' (POST): Открыт для **всех**
  - Вход в аккаунт
- 'logout' (DELETE): Открыт для **всех**
  - Выход с аккаунта
- 'verification/{user_id}': Открыт для **всех**
  - Верификация аккаунта, проходя по ссылке из письма на почте

### Hello world (`/hello_world`)
- 'user' (GET): Открыт для **user**
  - return: Hello world by user
- 'admin' (GET): Открыт для **admin**
  - return: Hello world by admin

## Файловая структура

```
.
├── conf # конфиги
├── docs # документация
└── src
    └── auth
        ├── application # логика приложения и интерфейсы
        ├── domain # модели
        ├── entrypoint # настройка запуска
        ├── infrastructure # адаптеры
        └── presentation # внешнее общение

```

## Описание схем реляционной базы данных
Использован императивный подход. С помощью `map_imperatively` была смаплена доменная модель в представление базы данных.

## Зависимости
Приложение разделено на слои:
1. Domain
2. Application
3. Infrastructure
4. Presentation

<p align="center">
  <img src="docs/CA.jpg" alt="Correct Dependency with DI" />
  <br><em>Чистая архитектура, Роберт Мартин</em>
</p>

- Соблюден принцип инверсии зависимотей
- Зависимости доставляются при помощи инъекции зависимостей, используя di-framework Dishka

## Проект использует переменные окружения, их нужно установить:
```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASS=123

BACKEND_PORT=8000

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_TTL=30000

SESSION_EXPIRATION_MINUTES=1

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_EMAIL_SENDER_QUEUE=email_sender_queue

RABBITMQ_PORT_ADMIN=15672

```

## Как запустить
1. Склонируй проект
2. Заполни переменные окружения
3. Подними проект ``docker compose up --build``
4. Проведи миграции. Либо напрямую в контейнере, либо ``make migrate`` в терминале

## Полезные материалы
1. Web sessions - https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
2. OAuth2 - https://auth0.com/docs и https://oauth.net/
