# Важно⚠️
**Проект написан специально для моего [Ютуб канала | Паша в мире АйТи](https://www.youtube.com/@PashaVmireIT) \
Если ты не видел теорию, а также процесс написания данного проекта – быстрее беги [смотреть](https://www.youtube.com/@PashaVmireIT)**

# Введение
Проект, реализующий работу с веб сессиями.\
❗**У проекта есть НЕСКОЛЬКО веток**. Каждая ветка является дополнением к main.

# Проект
## Технологический стек
- **Python**: `3.12`
- **Production**: `alembic`, `dishka`, `fastapi`, `psycopg`, `sqlalchemy[async]`, `gunicorn`
- **Development**: `isort`, `ruff`, `pre-commit`


## API
<p align="center">
  <img src="docs/API.jpg" />
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
# POSTGRES settings
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASS=

# API settings
BACKEND_PORT=

# SESSION settings
SESSION_EXPIRATION_MINUTES=
```

## Как запустить
1. Склонируй проект
2. Заполни переменные окружения
3. Подними проект ``docker compose up --build``
4. Проведи миграции. Либо напрямую в контейнере, либо ``make migrate`` в терминале

## Полезные материалы
1. Web sessions - https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
2. OAuth2 - https://auth0.com/docs и https://oauth.net/
