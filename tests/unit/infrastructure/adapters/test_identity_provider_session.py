from collections.abc import Iterator
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.domain.entities.session import Session
from auth.domain.entities.user import User
from auth.entrypoint.config import SessionConfig
from auth.infrastructure.adapters.identity_provider_session import (
    IdentityProviderSession,
)
from tests.conftest import FROZEN_NOW, STATIC_TOKEN, STATIC_TOKEN_HASH, CookieState


class TestIdentityProviderSession:
    @pytest.fixture(autouse=True)
    def frozen_clock(self) -> Iterator[None]:
        with patch(
            "auth.infrastructure.adapters.identity_provider_session.datetime"
        ) as clock:
            clock.now.return_value = FROZEN_NOW
            yield

    @pytest.fixture
    def identity_provider(
        self,
        mock_session_gateway: AsyncMock,
        mock_transport: AsyncMock,
        mock_transaction_manager: AsyncMock,
        mock_user_gateway: AsyncMock,
        session_config: SessionConfig,
    ) -> IdentityProviderSession:
        return IdentityProviderSession(
            session_data_gateway=mock_session_gateway,
            client_session_transport=mock_transport,
            session_token_hasher=MagicMock(
                spec=SessionTokenHasher, hash=lambda token: STATIC_TOKEN_HASH
            ),
            session_config=session_config,
            transaction_manager=mock_transaction_manager,
            user_data_gateway=mock_user_gateway,
        )

    @pytest.fixture
    def existing_session(
        self,
        mock_transport: AsyncMock,
        mock_session_gateway: AsyncMock,
        mock_user_gateway: AsyncMock,
        sample_session: Session,
        sample_user: User,
        saved_sessions: list[Session],
    ) -> Session:
        saved_sessions.append(sample_session)
        mock_transport.get_session.return_value = STATIC_TOKEN
        mock_session_gateway.read_by_token_hash.return_value = sample_session
        mock_user_gateway.read_by_id.return_value = sample_user
        return sample_session

    async def test_without_cookie_is_anonymous(
        self, identity_provider: IdentityProviderSession, cookie_state: CookieState
    ) -> None:
        user = await identity_provider.get_current_user()

        assert user is None
        assert cookie_state.deleted is False

    async def test_unknown_token_clears_cookie(
        self,
        identity_provider: IdentityProviderSession,
        mock_transport: AsyncMock,
        cookie_state: CookieState,
    ) -> None:
        mock_transport.get_session.return_value = STATIC_TOKEN

        user = await identity_provider.get_current_user()

        assert user is None
        assert cookie_state.deleted is True

    @pytest.mark.parametrize(
        "remaining_minutes",
        [pytest.param(-1, id="expired"), pytest.param(0, id="expires_now")],
    )
    async def test_expired_session_is_removed(
        self,
        identity_provider: IdentityProviderSession,
        existing_session: Session,
        saved_sessions: list[Session],
        cookie_state: CookieState,
        remaining_minutes: int,
    ) -> None:
        existing_session.expires_at = FROZEN_NOW + timedelta(minutes=remaining_minutes)

        user = await identity_provider.get_current_user()

        assert user is None
        assert saved_sessions == []
        assert cookie_state.deleted is True

    @pytest.mark.parametrize("remaining_minutes", [14, 15])
    async def test_session_is_renewed_at_or_below_half_lifetime(
        self,
        identity_provider: IdentityProviderSession,
        existing_session: Session,
        sample_user: User,
        cookie_state: CookieState,
        remaining_minutes: int,
    ) -> None:
        existing_session.expires_at = FROZEN_NOW + timedelta(minutes=remaining_minutes)

        user = await identity_provider.get_current_user()

        assert user == sample_user
        assert existing_session.expires_at == FROZEN_NOW + timedelta(minutes=30)
        assert cookie_state.token == STATIC_TOKEN
        assert cookie_state.deleted is False

    @pytest.mark.parametrize("remaining_minutes", [16, 30])
    async def test_fresh_session_is_not_renewed(
        self,
        identity_provider: IdentityProviderSession,
        existing_session: Session,
        sample_user: User,
        cookie_state: CookieState,
        remaining_minutes: int,
    ) -> None:
        expiration = FROZEN_NOW + timedelta(minutes=remaining_minutes)
        existing_session.expires_at = expiration

        user = await identity_provider.get_current_user()

        assert user == sample_user
        assert existing_session.expires_at == expiration
        assert cookie_state.token is None
        assert cookie_state.deleted is False

    @pytest.mark.parametrize(
        "missing_user",
        [pytest.param(True, id="missing"), pytest.param(False, id="inactive")],
    )
    async def test_missing_or_inactive_user_invalidates_session(
        self,
        identity_provider: IdentityProviderSession,
        existing_session: Session,
        mock_user_gateway: AsyncMock,
        inactive_user: User,
        saved_sessions: list[Session],
        cookie_state: CookieState,
        missing_user: bool,
    ) -> None:
        mock_user_gateway.read_by_id.return_value = (
            None if missing_user else inactive_user
        )

        user = await identity_provider.get_current_user()

        assert user is None
        assert saved_sessions == []
        assert cookie_state.deleted is True

    async def test_failed_renewal_does_not_refresh_cookie(
        self,
        identity_provider: IdentityProviderSession,
        existing_session: Session,
        mock_transaction_manager: AsyncMock,
        cookie_state: CookieState,
    ) -> None:
        existing_session.expires_at = FROZEN_NOW + timedelta(minutes=1)
        mock_transaction_manager.commit.side_effect = RuntimeError("commit failed")

        with pytest.raises(RuntimeError, match="commit failed"):
            await identity_provider.get_current_user()

        assert cookie_state.token is None
