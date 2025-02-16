from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.user import User, UserId, UserName
from auth.domain.user_role import UserRoleEnum


class UserDataMapperSqla(UserDataGateway):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(user)

    async def read_by_id(self, user_id: UserId) -> User | None:
        stmt = select(User).where(eq(User.id, user_id))

        user: User | None = (await self._session.execute(stmt)).scalar_one_or_none()

        return user

    async def read_by_username(self, username: UserName) -> User | None:
        stmt = select(User).where(eq(User.username, username))

        user = (await self._session.execute(stmt)).scalar_one_or_none()

        return user

    async def get_role(self, user_id: UserId) -> UserRoleEnum | None:
        user: User | None = await self._session.get(User, user_id)

        return user.role
