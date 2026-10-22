from typing import AsyncIterable, cast

from dishka import Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.requests import Request

from auth.application.interfaces.client_session_transport import ClientSessionTransport
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.password_hasher import PasswordHasher
from auth.application.interfaces.sender_letter import SenderLetter
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.application.interfaces.session_token_generator import SessionTokenGenerator
from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.entrypoint.config import Config, RabbitMQConfig, SessionConfig
from auth.infrastructure.adapters.email_sender_letter import EmailSenderLetter
from auth.infrastructure.adapters.identity_provider_session import (
    IdentityProviderSession,
)
from auth.infrastructure.adapters.password_hasher_argon2 import PasswordHasherArgon2
from auth.infrastructure.adapters.session_data_mapper_sqla import SessionDataMapperSqla
from auth.infrastructure.adapters.session_id_generator_uuid import (
    SessionIdGeneratorUuid,
)
from auth.infrastructure.adapters.session_token_generator_secrets import (
    SessionTokenGeneratorSecrets,
)
from auth.infrastructure.adapters.session_token_hasher_hmac_sha256 import (
    SessionTokenHasherHmacSha256,
)
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla
from auth.infrastructure.adapters.user_id_generator_uuid import UserIdGeneratorImpl
from auth.presentation.http.adapters.client_session_transport_cookie import (
    ClientSessionTransportCookie,
)
from auth.presentation.http.base.cookie_params import CookieParams, SameSite


class SqlaProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncEngine)
    async def provide_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(config.postgres_config.uri)
        try:
            yield engine
        finally:
            await engine.dispose()

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
    session_data_mapper = provide(
        SessionDataMapperSqla,
        scope=Scope.REQUEST,
        provides=SessionDataGateway,
    )


class IdGeneratorsProvider(Provider):
    session_id_generator = provide(
        SessionIdGeneratorUuid, scope=Scope.APP, provides=SessionIdGenerator
    )
    user_id_generator = provide(
        UserIdGeneratorImpl, scope=Scope.REQUEST, provides=UserIdGenerator
    )


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_cookie_params(self, session_config: SessionConfig) -> CookieParams:
        return CookieParams(
            max_age=session_config.expiration_minutes * 60,
            name=session_config.cookie_name,
            secure=session_config.cookie_secure,
            samesite=cast(SameSite, session_config.cookie_samesite),
        )

    request = from_context(provides=Request, scope=Scope.REQUEST)

    client_session_transport = provide(
        ClientSessionTransportCookie,
        scope=Scope.REQUEST,
        provides=ClientSessionTransport,
    )
    identity_provider = provide(
        IdentityProviderSession, scope=Scope.REQUEST, provides=IdentityProvider
    )
    session_token_generator = provide(
        SessionTokenGeneratorSecrets, scope=Scope.APP, provides=SessionTokenGenerator
    )
    session_token_hasher = provide(
        SessionTokenHasherHmacSha256, scope=Scope.APP, provides=SessionTokenHasher
    )

    password_hasher = provide(
        PasswordHasherArgon2, scope=Scope.REQUEST, provides=PasswordHasher
    )

    email_sender_letter = provide(
        EmailSenderLetter,
        scope=Scope.REQUEST,
        provides=SenderLetter,
    )


class RabbitMQProvider(Provider):
    broker = from_context(provides=RabbitBroker, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def provide_rabbitmq_config(self, config: Config) -> RabbitMQConfig:
        return config.rabbitmq_config


class ConfigProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def provide_session_config(self, config: Config) -> SessionConfig:
        return config.session_config
