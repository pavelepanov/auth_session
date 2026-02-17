import pytest
from unittest.mock import AsyncMock, MagicMock

from auth.application.errors import AuthenticationError, DoesNotExists, LogInError
from auth.application.interactors.log_in import LogInInteractor, LogInRequest
from auth.domain.entities.user import User


class TestLogInInteractor:

    @pytest.fixture
    def interactor(
        self,
        mock_identity_provider: AsyncMock,
        mock_user_data_gateway: AsyncMock,
        mock_session_data_gateway: AsyncMock,
        mock_request_manager: MagicMock,
        mock_session_id_generator: MagicMock,
        mock_password_hasher: MagicMock,
        session_config: MagicMock,
        mock_transaction_manager: AsyncMock,
    ) -> LogInInteractor:
        return LogInInteractor(
            identity_provider=mock_identity_provider,
            user_data_gateway=mock_user_data_gateway,
            session_data_gateway=mock_session_data_gateway,
            request_manager=mock_request_manager,
            session_id_generator=mock_session_id_generator,
            password_hasher=mock_password_hasher,
            session_config=session_config,
            transaction_manager=mock_transaction_manager,
        )

    async def test_successful_login(
        self,
        interactor: LogInInteractor,
        mock_user_data_gateway: AsyncMock,
        mock_session_data_gateway: AsyncMock,
        mock_request_manager: MagicMock,
        mock_transaction_manager: AsyncMock,
        sample_user: User,
    ):
        mock_user_data_gateway.read_by_username.return_value = sample_user

        request = LogInRequest(username="testuser", raw_password="ValidPass1")

        result = await interactor(request)
        assert result is None

        mock_session_data_gateway.add.assert_called_once()
        mock_request_manager.add_session_id_to_request.assert_called_once()
        mock_transaction_manager.commit.assert_called_once()

    async def test_login_fails_if_already_authenticated(
        self,
        interactor: LogInInteractor,
        mock_identity_provider: AsyncMock,
    ):
        mock_identity_provider.is_authenticated.return_value = True

        request = LogInRequest(username="testuser", raw_password="ValidPass1")

        with pytest.raises(LogInError):
            await interactor(request)

    async def test_login_fails_if_user_not_found(
        self,
        interactor: LogInInteractor,
    ):
        request = LogInRequest(username="nobody", raw_password="ValidPass1")

        with pytest.raises(DoesNotExists):
            await interactor(request)

    async def test_login_fails_with_wrong_password(
        self,
        interactor: LogInInteractor,
        mock_user_data_gateway: AsyncMock,
        mock_password_hasher: MagicMock,
        sample_user: User,
    ):
        mock_user_data_gateway.read_by_username.return_value = sample_user
        mock_password_hasher.is_password_valid.return_value = False

        request = LogInRequest(username="testuser", raw_password="WrongPass1")

        with pytest.raises(AuthenticationError):
            await interactor(request)

    async def test_login_fails_if_account_inactive(
        self,
        interactor: LogInInteractor,
        mock_user_data_gateway: AsyncMock,
        inactive_user: User,
    ):
        mock_user_data_gateway.read_by_username.return_value = inactive_user

        request = LogInRequest(username="inactive_user", raw_password="ValidPass1")

        with pytest.raises(AuthenticationError):
            await interactor(request)
