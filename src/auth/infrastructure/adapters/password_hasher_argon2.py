from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from auth.application.interfaces.password_hasher import PasswordHasher
from auth.domain.entities.user import PasswordHash, RawPassword, User


class PasswordHasherArgon2(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher()

    def hash(self, raw_password: RawPassword) -> PasswordHash:
        return PasswordHash(self._hasher.hash(raw_password))

    def verify(self, raw_password: RawPassword, password_hash: PasswordHash) -> bool:
        try:
            return self._hasher.verify(password_hash, raw_password)
        except VerificationError, InvalidHashError, UnicodeEncodeError:
            return False

    def is_password_valid(self, user: User, raw_password: RawPassword) -> bool:
        return self.verify(raw_password=raw_password, password_hash=user.password_hash)
