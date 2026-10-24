from unittest.mock import AsyncMock, MagicMock

import pytest

from auth.application.interactors.log_out import LogOutInteractor
from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.domain.entities.session import Session
from tests.conftest import STATIC_TOKEN, STATIC_TOKEN_HASH, CookieState


class TestLogOutInteractor:
    @pytest.fixture
    def interactor(
        self,
        mock_session_gateway: AsyncMock,
        mock_transport: AsyncMock,
        mock_transaction_manager: AsyncMock,
    ) -> LogOutInteractor:
        return LogOutInteractor(
            session_data_gateway=mock_session_gateway,
            client_session_transport=mock_transport,
            session_token_hasher=MagicMock(
                spec=SessionTokenHasher, hash=lambda token: STATIC_TOKEN_HASH
            ),
            transaction_manager=mock_transaction_manager,
        )

    @pytest.mark.parametrize("session_exists", [True, False])
    async def test_logout_removes_current_session_and_cookie(
        self,
        interactor: LogOutInteractor,
        mock_session_gateway: AsyncMock,
        mock_transport: AsyncMock,
        sample_session: Session,
        saved_sessions: list[Session],
        cookie_state: CookieState,
        session_exists: bool,
    ) -> None:
        mock_transport.get_session.return_value = STATIC_TOKEN
        mock_session_gateway.read_by_token_hash.return_value = (
            sample_session if session_exists else None
        )
        if session_exists:
            saved_sessions.append(sample_session)
        cookie_state.token = STATIC_TOKEN

        await interactor()

        assert saved_sessions == []
        assert cookie_state.token is None
        assert cookie_state.deleted is True

    async def test_failed_commit_preserves_client_cookie(
        self,
        interactor: LogOutInteractor,
        mock_session_gateway: AsyncMock,
        mock_transport: AsyncMock,
        mock_transaction_manager: AsyncMock,
        sample_session: Session,
        saved_sessions: list[Session],
        cookie_state: CookieState,
    ) -> None:
        saved_sessions.append(sample_session)
        mock_transport.get_session.return_value = STATIC_TOKEN
        mock_session_gateway.read_by_token_hash.return_value = sample_session
        mock_transaction_manager.commit.side_effect = RuntimeError("commit failed")
        cookie_state.token = STATIC_TOKEN

        with pytest.raises(RuntimeError, match="commit failed"):
            await interactor()

        assert cookie_state.token == STATIC_TOKEN
        assert cookie_state.deleted is False
