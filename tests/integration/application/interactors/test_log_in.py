from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.interactors.log_in import LogInInteractor, LogInRequest
from auth.domain.entities.session import Session
from auth.domain.entities.user import User
from auth.entrypoint.config import SessionConfig
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
from tests.conftest import PLAIN_PASSWORD, CookieState


class TestLogInInteractor:
    @pytest.fixture
    def interactor(
        self,
        mock_identity_provider: AsyncMock,
        user_gateway: UserDataMapperSqla,
        session_gateway: SessionDataMapperSqla,
        mock_transport: AsyncMock,
        password_hasher: PasswordHasherArgon2,
        session_config: SessionConfig,
        transaction_manager: TransactionManagerImpl,
    ) -> LogInInteractor:
        return LogInInteractor(
            identity_provider=mock_identity_provider,
            user_data_gateway=user_gateway,
            session_data_gateway=session_gateway,
            client_session_transport=mock_transport,
            session_id_generator=SessionIdGeneratorUuid(),
            session_token_generator=SessionTokenGeneratorSecrets(),
            session_token_hasher=SessionTokenHasherHmacSha256(session_config),
            password_hasher=password_hasher,
            session_config=session_config,
            transaction_manager=transaction_manager,
        )

    async def test_login_persists_only_hash_and_allows_multiple_sessions(
        self,
        interactor: LogInInteractor,
        db_session: AsyncSession,
        sample_user: User,
        cookie_state: CookieState,
        session_config: SessionConfig,
    ) -> None:
        db_session.add(sample_user)
        await db_session.commit()
        before = datetime.now(UTC)

        await interactor(LogInRequest(" TEST@EXAMPLE.COM ", PLAIN_PASSWORD))
        first_token = cookie_state.token
        await interactor(LogInRequest("test@example.com", PLAIN_PASSWORD))
        sessions = (await db_session.scalars(select(Session))).all()

        assert len(sessions) == 2
        assert first_token is not None
        assert cookie_state.token is not None
        assert first_token != cookie_state.token
        hasher = SessionTokenHasherHmacSha256(session_config)
        assert {session.token_hash for session in sessions} == {
            hasher.hash(first_token),
            hasher.hash(cookie_state.token),
        }
        for session in sessions:
            assert session.user_id == sample_user.id
            assert str(session.token_hash) not in {
                str(first_token),
                str(cookie_state.token),
            }
            assert before <= session.created_at <= datetime.now(UTC)
            assert session.expires_at >= before + timedelta(minutes=30)
