from auth.domain.entities.user import (PasswordHash, RawPassword, User, UserId,
                                       UserName)
from auth.domain.interfaces.password_hasher import PasswordHasher


class UserService:
    def __init__(
        self,
        password_hasher: PasswordHasher,
    ):
        self._password_hasher = password_hasher

    def create_user(
        self, id: UserId, username: UserName, password_hash: PasswordHash
    ) -> User:
        return User(
            id=id,
            username=username,
            password_hash=password_hash,
            is_active=True,
        )

    def is_password_valid(self, user: User, raw_password: RawPassword):
        return self._password_hasher.verify(
            raw_password=raw_password, password_hash=user.password_hash
        )
