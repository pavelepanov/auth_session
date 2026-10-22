from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.domain.entities.session import Session, SessionTokenHash


class SessionDataMapperSqla(SessionDataGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, session: Session) -> None:
        self._session.add(session)

    async def read_by_token_hash(self, token_hash: SessionTokenHash) -> Session | None:
        stmt = select(Session).where(eq(Session.token_hash, token_hash))
        return (await self._session.execute(stmt)).scalar_one_or_none()

    async def delete(self, session: Session) -> None:
        await self._session.delete(session)

    async def prolong(self, session: Session, expires_at: datetime) -> None:
        session.expires_at = expires_at
