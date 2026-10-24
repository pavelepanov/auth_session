from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.interactors.sign_up import SignUpInteractor, SignUpRequest
from auth.domain.entities.user import RawPassword, User
from auth.infrastructure.adapters.password_hasher_argon2 import PasswordHasherArgon2
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla
from auth.infrastructure.adapters.user_id_generator_uuid import UserIdGeneratorImpl
from tests.conftest import PLAIN_PASSWORD


class TestSignUpInteractor:
    @pytest.fixture
    def interactor(
        self,
        mock_identity_provider: AsyncMock,
        user_gateway: UserDataMapperSqla,
        transaction_manager: TransactionManagerImpl,
        password_hasher: PasswordHasherArgon2,
    ) -> SignUpInteractor:
        return SignUpInteractor(
            identity_provider=mock_identity_provider,
            user_data_gateway=user_gateway,
            transaction_manager=transaction_manager,
            password_hasher=password_hasher,
            user_id_generator=UserIdGeneratorImpl(),
        )

    async def test_signup_persists_normalized_user_with_argon2_password(
        self,
        interactor: SignUpInteractor,
        db_session: AsyncSession,
        password_hasher: PasswordHasherArgon2,
    ) -> None:
        response = await interactor(SignUpRequest(" TEST@EXAMPLE.COM ", PLAIN_PASSWORD))
        db_session.expunge_all()

        user = await db_session.get(User, response.id)

        assert user is not None
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert [role.value for role in user.roles] == ["user"]
        assert user.password_hash.startswith("$argon2id$")
        assert password_hasher.verify(RawPassword(PLAIN_PASSWORD), user.password_hash)
