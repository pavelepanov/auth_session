from typing import AsyncIterable
from redis import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dishka import Provider, Scope, from_context, provide
from auth.entrypoint.config import PostgresConfig, RedisConfig
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl

from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla

from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.infrastructure.adapters.session_id_generator_str import SessionIdGeneratorImpl

from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.infrastructure.adapters.user_id_generator_uuid import UserIdGeneratorImpl

from auth.application.interfaces.session_manager import SessionManager
from auth.infrastructure.adapters.session_manager_redis import SessionManagerRedis

from auth.presentation.http.base.cookie_params import CookieParams

from starlette.requests import Request

from auth.application.interfaces.request_manager import RequestManager
from auth.presentation.http.middlewares.request_manager_cookie import RequestManagerCookie

from auth.application.interfaces.identity_provider import IdentityProvider
from auth.infrastructure.adapters.identity_provider_sqla import IdentityProviderSession


class SqlaProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self, config: PostgresConfig) -> AsyncEngine:
        return create_async_engine(config.postgres_config.db_uri)

    @provide(scope=Scope.APP)
    def provide_sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    transaction_manager = provide(TransactionManagerImpl, scope=Scope.REQUEST, provides=TransactionManager)
    user_data_mapper = provide(UserDataMapperSqla, scope=Scope.REQUEST, provides=UserDataGateway)
    identity_provider = provide(IdentityProviderSession, scope=Scope.REQUEST, provides=IdentityProvider)


class IdGeneratorsProvider(Provider):
    session_id_generator = provide(SessionIdGeneratorImpl, scope=Scope.REQUEST, provides=SessionIdGenerator)
    user_id_generator = provide(UserIdGeneratorImpl, scope=Scope.REQUEST, provides=UserIdGenerator)


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_redis_client(self, config: RedisConfig) -> Redis:
        return Redis(
            host=config.host, port=config.port, decode_responses=True,
        )

    session_manager = provide(SessionManagerRedis, scope=Scope.REQUEST, provides=SessionManager)


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_cookie_params(self) -> CookieParams:
        is_cookie_secure: bool = True
        if is_cookie_secure:
            return CookieParams(secure=True, samesite="strict")
        return CookieParams(secure=False)

    request = from_context(provides=Request, scope=Scope.REQUEST)

    request_manager = provide(RequestManagerCookie, scope=Scope.REQUEST, provides=RequestManager)
