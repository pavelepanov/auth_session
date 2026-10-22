from psycopg.errors import UniqueViolation
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.errors import AlreadyExists
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.user import User, UserEmail, UserId


class UserDataMapperSqla(UserDataGateway):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(user)
        try:
            await self._session.flush()
        except IntegrityError as error:
            if (
                isinstance(error.orig, UniqueViolation)
                and error.orig.diag.constraint_name == "uq_users_email_lower_btrim"
            ):
                raise AlreadyExists("User with this email already exists.") from error
            raise

    async def read_by_id(self, user_id: UserId) -> User | None:
        user: User | None = await self._session.get(User, user_id)

        return user

    async def read_by_email(self, email: UserEmail) -> User | None:
        normalized_email = email.strip().lower()
        stmt = select(User).where(
            func.lower(func.btrim(User.email)) == normalized_email
        )

        user = (await self._session.execute(stmt)).scalar_one_or_none()

        return user
