"""HTTP contract and full-stack clients sharing the production HTTP setup."""

from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import cast
from unittest.mock import AsyncMock

import pytest
from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from auth.application.interactors.admin_hello_world import (
    AdminHelloWorldInteractor,
    AdminHelloWorldResponse,
)
from auth.application.interactors.log_in import LogInInteractor
from auth.application.interactors.log_out import LogOutInteractor
from auth.application.interactors.sign_up import SignUpInteractor, SignUpResponse
from auth.application.interactors.user_hello_world import (
    UserHelloWorldInteractor,
    UserHelloWorldResponse,
)
from auth.entrypoint.config import Config, PostgresConfig, SessionConfig
from auth.entrypoint.ioc.registry import get_providers
from auth.entrypoint.setup import configure_app, create_app, create_async_ioc_container
from auth.presentation.http.base.root_router import root_router
from tests.conftest import STATIC_USER_ID


@asynccontextmanager
async def http_client(
    providers: Iterable[Provider], config: Config
) -> AsyncIterator[AsyncClient]:
    """Build the real HTTP layer; providers choose mocked or real use cases."""
    container = create_async_ioc_container(providers, config)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await container.close()

    app = create_app(lifespan)
    configure_app(app, root_router)
    setup_dishka(container, app)
    async with (
        app.router.lifespan_context(app),
        AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="https://testserver",
        ) as client,
    ):
        yield client


@dataclass
class InteractorMocks:
    login: AsyncMock
    logout: AsyncMock
    signup: AsyncMock
    user: AsyncMock
    admin: AsyncMock


class MockInteractorProvider(Provider):
    def __init__(self, mocks: InteractorMocks) -> None:
        super().__init__()
        self.mocks = mocks

    @provide(scope=Scope.REQUEST, override=True)
    def login(self) -> LogInInteractor:
        return cast(LogInInteractor, self.mocks.login)

    @provide(scope=Scope.REQUEST, override=True)
    def logout(self) -> LogOutInteractor:
        return cast(LogOutInteractor, self.mocks.logout)

    @provide(scope=Scope.REQUEST, override=True)
    def signup(self) -> SignUpInteractor:
        return cast(SignUpInteractor, self.mocks.signup)

    @provide(scope=Scope.REQUEST, override=True)
    def user(self) -> UserHelloWorldInteractor:
        return cast(UserHelloWorldInteractor, self.mocks.user)

    @provide(scope=Scope.REQUEST, override=True)
    def admin(self) -> AdminHelloWorldInteractor:
        return cast(AdminHelloWorldInteractor, self.mocks.admin)


class TestSessionProvider(Provider):
    __test__ = False

    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        super().__init__()
        self.factory = factory

    @provide(scope=Scope.APP, override=True)
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        return self.factory


@pytest.fixture
def test_config(session_config: SessionConfig) -> Config:
    return Config(
        postgres_config=PostgresConfig(
            host="127.0.0.1",
            port=55432,
            db="unused",
            user="auth_test",
            password="auth_test",
            uri="postgresql+psycopg://auth_test:auth_test@127.0.0.1:55432/unused",
        ),
        session_config=session_config,
    )


@pytest.fixture
def interactor_mocks() -> InteractorMocks:
    return InteractorMocks(
        login=AsyncMock(spec=LogInInteractor, return_value=None),
        logout=AsyncMock(spec=LogOutInteractor, return_value=None),
        signup=AsyncMock(
            spec=SignUpInteractor, return_value=SignUpResponse(STATIC_USER_ID)
        ),
        user=AsyncMock(
            spec=UserHelloWorldInteractor,
            return_value=UserHelloWorldResponse("hello world by user"),
        ),
        admin=AsyncMock(
            spec=AdminHelloWorldInteractor,
            return_value=AdminHelloWorldResponse("hello world by admin"),
        ),
    )


@pytest.fixture
async def client(
    interactor_mocks: InteractorMocks, test_config: Config
) -> AsyncIterator[AsyncClient]:
    providers = (*get_providers(), MockInteractorProvider(interactor_mocks))
    async with http_client(providers, test_config) as client:
        yield client


@pytest.fixture
async def full_client(
    sessionmaker: async_sessionmaker[AsyncSession], test_config: Config
) -> AsyncIterator[AsyncClient]:
    providers = (*get_providers(), TestSessionProvider(sessionmaker))
    async with http_client(providers, test_config) as client:
        yield client
