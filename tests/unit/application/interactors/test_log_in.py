from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auth.application.errors import AlreadyAuthenticatedError, InvalidCredentialsError
from auth.application.interactors.log_in import LogInInteractor, LogInRequest
from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.application.interfaces.session_token_generator import SessionTokenGenerator
from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.domain.entities.session import Session
from auth.domain.entities.user import RawPassword, User, UserEmail
from auth.entrypoint.config import SessionConfig
from tests.conftest import (
    FROZEN_NOW,
    PLAIN_PASSWORD,
    STATIC_SESSION_ID,
    STATIC_TOKEN,
    STATIC_TOKEN_HASH,
    CookieState,
)


class TestLogInInteractor:
    @pytest.fixture
    def interactor(
        self,
        mock_identity_provider: AsyncMock,
        mock_user_gateway: AsyncMock,
        mock_session_gateway: AsyncMock,
        mock_transport: AsyncMock,
        mock_transaction_manager: AsyncMock,
        mock_password_hasher: MagicMock,
        session_config: SessionConfig,
    ) -> LogInInteractor:
        return LogInInteractor(
            identity_provider=mock_identity_provider,
            user_data_gateway=mock_user_gateway,
            session_data_gateway=mock_session_gateway,
            client_session_transport=mock_transport,
            session_id_generator=MagicMock(
                spec=SessionIdGenerator, return_value=STATIC_SESSION_ID
            ),
            session_token_generator=MagicMock(
                spec=SessionTokenGenerator, generate=lambda: STATIC_TOKEN
            ),
            session_token_hasher=MagicMock(
                spec=SessionTokenHasher, hash=lambda token: STATIC_TOKEN_HASH
            ),
            password_hasher=mock_password_hasher,
            session_config=session_config,
            transaction_manager=mock_transaction_manager,
        )

    async def test_success_creates_hashed_session_and_cookie(
        self,
        interactor: LogInInteractor,
        mock_user_gateway: AsyncMock,
        sample_user: User,
        saved_sessions: list[Session],
        cookie_state: CookieState,
    ) -> None:
        mock_user_gateway.read_by_email.return_value = sample_user

        with patch("auth.application.interactors.log_in.datetime") as clock:
            clock.now.return_value = FROZEN_NOW
            await interactor(LogInRequest("test@example.com", PLAIN_PASSWORD))

        assert len(saved_sessions) == 1
        session = saved_sessions[0]
        assert session.user_id == sample_user.id
        assert session.token_hash == STATIC_TOKEN_HASH
        assert session.expires_at == FROZEN_NOW + timedelta(minutes=30)
        assert cookie_state.token == STATIC_TOKEN

    async def test_normalizes_credentials(
        self,
        interactor: LogInInteractor,
        mock_user_gateway: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
        cookie_state: CookieState,
    ) -> None:
        def lookup(email: UserEmail) -> User | None:
            return sample_user if email == "test@example.com" else None

        def verify(user: User, raw_password: RawPassword) -> bool:
            return user.id == sample_user.id and raw_password == "é" * 15

        mock_user_gateway.read_by_email.side_effect = lookup
        mock_password_hasher.is_password_valid.side_effect = verify

        await interactor(LogInRequest(" TEST@EXAMPLE.COM ", "e\u0301" * 15))

        assert cookie_state.token == STATIC_TOKEN

    async def test_already_authenticated(
        self,
        interactor: LogInInteractor,
        mock_identity_provider: AsyncMock,
        sample_user: User,
        saved_sessions: list[Session],
    ) -> None:
        mock_identity_provider.get_current_user.return_value = sample_user

        with pytest.raises(AlreadyAuthenticatedError):
            await interactor(LogInRequest("test@example.com", PLAIN_PASSWORD))

        assert saved_sessions == []

    @pytest.mark.parametrize(
        "reason", ["missing", "inactive", "wrong_password", "short"]
    )
    async def test_invalid_credentials_create_no_session(
        self,
        interactor: LogInInteractor,
        mock_user_gateway: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
        saved_sessions: list[Session],
        cookie_state: CookieState,
        reason: str,
    ) -> None:
        mock_user_gateway.read_by_email.return_value = (
            None if reason == "missing" else sample_user
        )
        sample_user.is_active = reason != "inactive"
        mock_password_hasher.is_password_valid.return_value = reason != "wrong_password"
        password = "short" if reason == "short" else PLAIN_PASSWORD

        with pytest.raises(InvalidCredentialsError):
            await interactor(LogInRequest("test@example.com", password))

        assert saved_sessions == []
        assert cookie_state.token is None

    async def test_failed_commit_does_not_issue_cookie(
        self,
        interactor: LogInInteractor,
        mock_user_gateway: AsyncMock,
        mock_transaction_manager: AsyncMock,
        sample_user: User,
        cookie_state: CookieState,
    ) -> None:
        mock_user_gateway.read_by_email.return_value = sample_user
        mock_transaction_manager.commit.side_effect = RuntimeError("commit failed")

        with pytest.raises(RuntimeError, match="commit failed"):
            await interactor(LogInRequest("test@example.com", PLAIN_PASSWORD))

        assert cookie_state.token is None
