from sqlalchemy.ext.asyncio import AsyncSession

from auth.application.interfaces.transaction_manager import TransactionManager


class TransactionManagerImpl(TransactionManager):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()
