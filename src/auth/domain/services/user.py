from auth.domain.entities.user import PasswordHash, User, UserId, UserName


class UserService:
    def create_user(
        self, id: UserId, username: UserName, password_hash: PasswordHash
    ) -> User:
        return User(
            id=id,
            username=username,
            password_hash=password_hash,
            is_active=True,
        )
