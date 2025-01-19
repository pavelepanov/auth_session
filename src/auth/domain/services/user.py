from auth.domain.entities.user import PasswordHash, User, UserId


class UserService:
    def create_user(self, id: UserId, password_hash: PasswordHash) -> User:
        return User(
            id=id,
            password_hash=password_hash,
            is_active=True,
        )
