"""Создаёт двух пользователей для локальной разработки и ручной проверки."""

import asyncio
from unicodedata import normalize
from uuid import uuid4

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from auth.application.validators.check_raw_password import check_valid_raw_password
from auth.domain.entities.user import (
    RawPassword,
    UserEmail,
    UserId,
    UserRoleEnum,
    create_user,
)
from auth.entrypoint.config import PostgresConfig
from auth.infrastructure.adapters.password_hasher_argon2 import PasswordHasherArgon2
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla
from auth.infrastructure.persistence_sqla.mappings.map import map_tables

DEMO_USERS = (
    ("admin@example.com", "admin-test-password", UserRoleEnum.ADMIN),
    ("user@example.com", "user-test-password", UserRoleEnum.USER),
)


async def seed_users() -> None:
    map_tables()
    engine = create_async_engine(PostgresConfig.from_env().uri)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    password_hasher = PasswordHasherArgon2()
    messages: list[str] = []

    try:
        async with sessionmaker.begin() as session:
            gateway = UserDataMapperSqla(session)
            try:
                roles = {
                    value: await gateway.get_role_by_value(value)
                    for value in UserRoleEnum
                }
            except NoResultFound as error:
                raise SystemExit(
                    "Перед созданием тестовых пользователей примените миграции Alembic."
                ) from error

            for email, password, role in DEMO_USERS:
                user_email = UserEmail(email.strip().lower())
                if await gateway.read_by_email(user_email) is not None:
                    messages.append(f"Пропущен {user_email}: уже существует.")
                    continue

                raw_password = RawPassword(normalize("NFC", password))
                if not check_valid_raw_password(raw_password):
                    raise ValueError(f"Некорректный тестовый пароль для {user_email}")
                password_hash = await asyncio.to_thread(
                    password_hasher.hash, raw_password
                )
                await gateway.add(
                    create_user(
                        id=UserId(uuid4()),
                        email=user_email,
                        password_hash=password_hash,
                        roles=[roles[role]],
                    )
                )
                messages.append(f"Создан {role.value}: {user_email} / {password}")
    finally:
        await engine.dispose()

    for message in messages:
        print(message)


if __name__ == "__main__":
    asyncio.run(seed_users())
