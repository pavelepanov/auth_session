import pytest
from unittest.mock import AsyncMock, MagicMock

from auth.application.errors import AlreadyExists, InvalidPassword, SignUpError
from auth.application.interactors.sign_up import (
    SignUpInteractor,
    SignUpRequest,
    SignUpResponse,
)
from auth.domain.entities.user import User


class TestSignUpInteractor:

    @pytest.fixture
    def interactor(
        self,
        mock_identity_provider: AsyncMock,
        mock_user_data_gateway: AsyncMock,
        mock_transaction_manager: AsyncMock,
        mock_password_hasher: MagicMock,
        mock_user_id_generator: MagicMock,
        mock_sender_letter: AsyncMock,
    ) -> SignUpInteractor:
        return SignUpInteractor(
            identity_provider=mock_identity_provider,
            user_data_gateway=mock_user_data_gateway,
            transaction_manager=mock_transaction_manager,
            password_hasher=mock_password_hasher,
            user_id_generator=mock_user_id_generator,
            sender_letter=mock_sender_letter,
        )

    async def test_successful_sign_up(
        self,
        interactor: SignUpInteractor,
        mock_user_data_gateway: AsyncMock,
        mock_transaction_manager: AsyncMock,
        mock_sender_letter: AsyncMock,
        user_id,
    ):
        request = SignUpRequest(username="newuser", raw_password="ValidPass1")

        result = await interactor(request)

        assert isinstance(result, SignUpResponse)
        assert result.id == user_id
        mock_user_data_gateway.add.assert_called_once()
        mock_sender_letter.send_letter.assert_called_once()
        mock_transaction_manager.commit.assert_called_once()

    async def test_sign_up_fails_if_already_authenticated(
        self,
        interactor: SignUpInteractor,
        mock_identity_provider: AsyncMock,
    ):
        mock_identity_provider.is_authenticated.return_value = True

        request = SignUpRequest(username="newuser", raw_password="ValidPass1")

        with pytest.raises(SignUpError):
            await interactor(request)

    async def test_sign_up_fails_if_username_already_exists(
        self,
        interactor: SignUpInteractor,
        mock_user_data_gateway: AsyncMock,
        sample_user: User,
    ):
        mock_user_data_gateway.read_by_username.return_value = sample_user

        request = SignUpRequest(username="testuser", raw_password="ValidPass1")

        with pytest.raises(AlreadyExists):
            await interactor(request)

    async def test_sign_up_fails_with_weak_password(
        self,
        interactor: SignUpInteractor,
    ):
        request = SignUpRequest(username="newuser", raw_password="weak")

        with pytest.raises(InvalidPassword):
            await interactor(request)
