import pytest

from auth.domain.entities.user import PasswordHash, RawPassword, User
from auth.infrastructure.adapters.password_hasher_argon2 import PasswordHasherArgon2
from tests.conftest import PLAIN_PASSWORD


class TestPasswordHasherArgon2:
    @pytest.fixture
    def hasher(self) -> PasswordHasherArgon2:
        return PasswordHasherArgon2()

    def test_hash_can_be_verified(self, hasher: PasswordHasherArgon2) -> None:
        hashed = hasher.hash(RawPassword(PLAIN_PASSWORD))

        assert hashed.startswith("$argon2id$")
        assert hashed != PLAIN_PASSWORD
        assert hasher.verify(RawPassword(PLAIN_PASSWORD), hashed) is True
        assert hasher.verify(RawPassword("another-password"), hashed) is False

    @pytest.mark.parametrize("hashed", ["", "broken", "$argon2id$invalid"])
    def test_malformed_hash_is_rejected(
        self, hasher: PasswordHasherArgon2, hashed: str
    ) -> None:
        assert hasher.verify(RawPassword(PLAIN_PASSWORD), PasswordHash(hashed)) is False

    def test_user_password_validation(
        self, hasher: PasswordHasherArgon2, sample_user: User
    ) -> None:
        sample_user.password_hash = hasher.hash(RawPassword(PLAIN_PASSWORD))

        assert (
            hasher.is_password_valid(sample_user, RawPassword(PLAIN_PASSWORD)) is True
        )
        assert hasher.is_password_valid(sample_user, RawPassword("\ud800")) is False
