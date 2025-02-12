from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId


class SessionDataMapperSqla(SessionDataGateway):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self._session = session

    async def add(self, session: Session) -> None:
        self._session.add(session)

    async def get_user_id(self, session_id: SessionId) -> UserId | None:
        stmt = select(Session).where(eq(Session.id, session_id))

        session: Session | None = (
            await self._session.execute(stmt)
        ).scalar_one_or_none()

        if session is None:
            return None

        return session.user_id

    async def delete_session(self, session_id: SessionId) -> None:
        session: Session | None = await self._session.get(Session, session_id)

        if session is None:
            return None

        await self._session.delete(session)

    async def prolong_expiration(
        self, session_id: SessionId, expiration: datetime
    ) -> None:
        session: Session | None = await self._session.get(Session, session_id)

        if session is None:
            return None

        session.expiration = expiration
