"""Lazy PostgreSQL startup, one migrated DB per worker, rollback per test."""

import asyncio
import hashlib
import os
import re
import subprocess
import sys
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import pytest
import pytest_asyncio
from filelock import FileLock
from sqlalchemy import NullPool, select, text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from auth.domain.entities.user import PasswordHash, RawPassword, Role, UserRoleEnum
from auth.infrastructure.adapters.password_hasher_argon2 import PasswordHasherArgon2
from auth.infrastructure.adapters.session_data_mapper_sqla import SessionDataMapperSqla
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla
from auth.infrastructure.persistence_sqla.mappings.map import map_tables
from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry
from tests.conftest import PLAIN_PASSWORD

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def postgres_service(tmp_path_factory: pytest.TempPathFactory, worker_id: str) -> None:
    """Start Compose only when a DB fixture is requested, once across workers."""
    if "TEST_POSTGRES_HOST" in os.environ:
        return
    shared_temp = tmp_path_factory.getbasetemp()
    if worker_id != "master":
        shared_temp = shared_temp.parent
    ready = shared_temp / "postgres.ready"
    with FileLock(str(shared_temp / "postgres.lock")):
        if ready.exists():
            return
        try:
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "--env-file",
                    "/dev/null",
                    "-f",
                    str(ROOT / "compose.test.yaml"),
                    "up",
                    "-d",
                    "--wait",
                    "--wait-timeout",
                    "60",
                ],
                cwd=ROOT,
                check=True,
                timeout=90,
            )
        except (OSError, subprocess.SubprocessError) as error:
            pytest.fail(
                "Не удалось запустить тестовый PostgreSQL. "
                "Проверьте Docker Desktop или задайте TEST_POSTGRES_*. "
                f"Причина: {error}",
                pytrace=False,
            )
        ready.touch()


@pytest.fixture(scope="session")
def mapped_tables() -> None:
    if not mapping_registry.mappers:
        map_tables()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_engine(
    postgres_service: None, mapped_tables: None, worker_id: str, testrun_uid: str
) -> AsyncIterator[AsyncEngine]:
    run_id = hashlib.sha256(testrun_uid.encode()).hexdigest()[:16]
    worker = re.sub(r"[^a-zA-Z0-9_]", "_", worker_id)[:12]
    database = f"auth_test_{run_id}_{worker}_{uuid4().hex[:8]}"
    admin_url = URL.create(
        "postgresql+psycopg",
        username=os.environ.get("TEST_POSTGRES_USER", "auth_test"),
        password=os.environ.get("TEST_POSTGRES_PASSWORD", "auth_test"),
        host=os.environ.get("TEST_POSTGRES_HOST", "127.0.0.1"),
        port=int(os.environ.get("TEST_POSTGRES_PORT", "55432")),
        database="postgres",
    )
    admin = create_async_engine(
        admin_url, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    engine = create_async_engine(admin_url.set(database=database), poolclass=NullPool)
    created = False
    try:
        async with admin.connect() as connection:
            await connection.execute(text(f'CREATE DATABASE "{database}"'))
        created = True
        environment = {
            **os.environ,
            "POSTGRES_HOST": str(admin_url.host),
            "POSTGRES_PORT": str(admin_url.port),
            "POSTGRES_USER": str(admin_url.username),
            "POSTGRES_PASS": str(admin_url.password),
            "POSTGRES_DB": database,
        }
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "alembic",
            "upgrade",
            "head",
            cwd=ROOT,
            env=environment,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        try:
            async with asyncio.timeout(60):
                output, _ = await process.communicate()
        finally:
            if process.returncode is None:
                process.kill()
                await process.communicate()
        if process.returncode:
            pytest.fail(f"Не удалось применить тестовые миграции:\n{output.decode()}")
        yield engine
    finally:
        await engine.dispose()
        try:
            if created:
                async with admin.connect() as connection:
                    await connection.execute(
                        text(f'DROP DATABASE "{database}" WITH (FORCE)')
                    )
        finally:
            await admin.dispose()


@pytest.fixture
async def db_connection(db_engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        try:
            yield connection
        finally:
            await transaction.rollback()


@pytest.fixture
def sessionmaker(
    db_connection: AsyncConnection,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


@pytest.fixture
async def db_session(
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with sessionmaker() as session:
        yield session


@pytest.fixture
async def user_role(db_session: AsyncSession) -> Role:
    return (
        await db_session.execute(select(Role).filter_by(value=UserRoleEnum.USER))
    ).scalar_one()


@pytest.fixture
async def admin_role(db_session: AsyncSession) -> Role:
    return (
        await db_session.execute(select(Role).filter_by(value=UserRoleEnum.ADMIN))
    ).scalar_one()


@pytest.fixture(scope="session")
def password_hash() -> PasswordHash:
    return PasswordHasherArgon2().hash(RawPassword(PLAIN_PASSWORD))


@pytest.fixture
def user_gateway(db_session: AsyncSession) -> UserDataMapperSqla:
    return UserDataMapperSqla(db_session)


@pytest.fixture
def session_gateway(db_session: AsyncSession) -> SessionDataMapperSqla:
    return SessionDataMapperSqla(db_session)


@pytest.fixture
def transaction_manager(db_session: AsyncSession) -> TransactionManagerImpl:
    return TransactionManagerImpl(db_session)


@pytest.fixture
def password_hasher() -> PasswordHasherArgon2:
    return PasswordHasherArgon2()
