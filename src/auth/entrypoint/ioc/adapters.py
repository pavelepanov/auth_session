from typing import AsyncIterable

from dishka import Provider, Scope, from_context, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.requests import Request

from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.application.interfaces.session_manager import SessionManager
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.domain.interfaces.password_hasher import PasswordHasher
from auth.domain.services.session import SessionService
from auth.domain.services.user import UserService
from auth.entrypoint.config import Config, RedisConfig
from auth.infrastructure.adapters.identity_provider_sqla import IdentityProviderSession
from auth.infrastructure.adapters.password_hasher_bcrypt import PasswordHasherBcrypt
from auth.infrastructure.adapters.session_id_generator_str import SessionIdGeneratorImpl
from auth.infrastructure.adapters.session_manager_redis import SessionManagerRedis
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla
from auth.infrastructure.adapters.user_id_generator_uuid import UserIdGeneratorImpl
from auth.presentation.http.base.cookie_params import CookieParams
from auth.presentation.http.middlewares.request_manager_cookie import (
    RequestManagerCookie,
)


class SqlaProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_engine(self, config: Config) -> AsyncEngine:
        return create_async_engine(config.postgres_config.uri)

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

    transaction_manager = provide(
        TransactionManagerImpl, scope=Scope.REQUEST, provides=TransactionManager
    )
    user_data_mapper = provide(
        UserDataMapperSqla, scope=Scope.REQUEST, provides=UserDataGateway
    )
    identity_provider = provide(
        IdentityProviderSession, scope=Scope.REQUEST, provides=IdentityProvider
    )


class IdGeneratorsProvider(Provider):
    session_id_generator = provide(
        SessionIdGeneratorImpl, scope=Scope.REQUEST, provides=SessionIdGenerator
    )
    user_id_generator = provide(
        UserIdGeneratorImpl, scope=Scope.REQUEST, provides=UserIdGenerator
    )


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_redis_client(self, config: Config) -> Redis:
        return Redis(
            host=config.redis_config.host,
            port=config.redis_config.port,
            decode_responses=True,
        )

    @provide(scope=Scope.APP)
    def provide_redis_config(self, config: Config) -> RedisConfig:
        return RedisConfig(
            host=config.redis_config.host,
            port=config.redis_config.port,
            ttl=config.redis_config.ttl,
        )

    session_manager = provide(
        SessionManagerRedis, scope=Scope.REQUEST, provides=SessionManager
    )


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_cookie_params(self) -> CookieParams:
        is_cookie_secure: bool = True
        if is_cookie_secure:
            return CookieParams(secure=True, samesite="strict")
        return CookieParams(secure=False)

    request = from_context(provides=Request, scope=Scope.REQUEST)

    request_manager = provide(
        RequestManagerCookie, scope=Scope.REQUEST, provides=RequestManager
    )

    password_hasher = provide(
        PasswordHasherBcrypt, scope=Scope.REQUEST, provides=PasswordHasher
    )


class ServicesProvider(Provider):
    session_service = provide(SessionService, scope=Scope.REQUEST)
    user_service = provide(UserService, scope=Scope.REQUEST)


class ConfigProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
