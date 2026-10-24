from unittest.mock import AsyncMock, MagicMock

import pytest

from auth.application.errors import (
    AlreadyAuthenticatedError,
    InvalidPasswordError,
    UserEmailAlreadyExistsError,
)
from auth.application.interactors.sign_up import SignUpInteractor, SignUpRequest
from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.domain.entities.user import PasswordHash, RawPassword, User
from tests.conftest import PLAIN_PASSWORD, STATIC_USER_ID


class TestSignUpInteractor:
    @pytest.fixture
    def interactor(
        self,
        mock_identity_provider: AsyncMock,
        mock_user_gateway: AsyncMock,
        mock_transaction_manager: AsyncMock,
        mock_password_hasher: MagicMock,
    ) -> SignUpInteractor:
        return SignUpInteractor(
            identity_provider=mock_identity_provider,
            user_data_gateway=mock_user_gateway,
            transaction_manager=mock_transaction_manager,
            password_hasher=mock_password_hasher,
            user_id_generator=MagicMock(
                spec=UserIdGenerator, return_value=STATIC_USER_ID
            ),
        )

    async def test_creates_active_user_with_normalized_email(
        self,
        interactor: SignUpInteractor,
        saved_users: list[User],
        password_hash: PasswordHash,
    ) -> None:
        request = SignUpRequest("  TEST@EXAMPLE.COM  ", PLAIN_PASSWORD)

        response = await interactor(request)

        assert response.id == STATIC_USER_ID
        assert len(saved_users) == 1
        user = saved_users[0]
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert [role.value for role in user.roles] == ["user"]
        assert user.password_hash == password_hash

    async def test_normalizes_unicode_before_hashing(
        self,
        interactor: SignUpInteractor,
        mock_password_hasher: MagicMock,
        saved_users: list[User],
    ) -> None:
        def hash_password(raw_password: RawPassword) -> PasswordHash:
            return PasswordHash(f"hash:{raw_password}")

        mock_password_hasher.hash.side_effect = hash_password

        await interactor(SignUpRequest("a@example.com", "e\u0301" * 15))

        assert saved_users[0].password_hash == "hash:" + "é" * 15

    async def test_rejects_authenticated_user(
        self,
        interactor: SignUpInteractor,
        mock_identity_provider: AsyncMock,
        sample_user: User,
        saved_users: list[User],
    ) -> None:
        mock_identity_provider.get_current_user.return_value = sample_user

        with pytest.raises(AlreadyAuthenticatedError):
            await interactor(SignUpRequest("a@example.com", PLAIN_PASSWORD))

        assert saved_users == []

    async def test_rejects_existing_email(
        self,
        interactor: SignUpInteractor,
        mock_user_gateway: AsyncMock,
        sample_user: User,
        saved_users: list[User],
    ) -> None:
        mock_user_gateway.read_by_email.return_value = sample_user

        with pytest.raises(UserEmailAlreadyExistsError):
            await interactor(SignUpRequest(str(sample_user.email), PLAIN_PASSWORD))

        assert saved_users == []

    async def test_rejects_invalid_password(
        self,
        interactor: SignUpInteractor,
        saved_users: list[User],
    ) -> None:
        with pytest.raises(InvalidPasswordError):
            await interactor(SignUpRequest("a@example.com", "short"))

        assert saved_users == []
