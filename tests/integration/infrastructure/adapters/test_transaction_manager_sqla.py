from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from auth.domain.entities.user import User
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl
from tests.conftest import STATIC_USER_ID


async def test_commit_persists_after_writer_closes(
    sessionmaker: async_sessionmaker[AsyncSession],
    sample_user: User,
) -> None:
    sample_user.roles = []
    async with sessionmaker() as writer:
        assert await writer.get(User, STATIC_USER_ID) is None
        writer.add(sample_user)

        await TransactionManagerImpl(writer).commit()

    # A flush without commit is rolled back when the writer closes.
    async with sessionmaker() as observer:
        found = await observer.get(User, STATIC_USER_ID)

        assert found is not None
        assert found.email == sample_user.email


async def test_outer_rollback_removes_committed_data(
    db_engine: AsyncEngine, sample_user: User
) -> None:
    # Use no role loaded by another test session on this independent connection.
    sample_user.roles = []
    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint"
        ) as session:
            session.add(sample_user)
            await TransactionManagerImpl(session).commit()
        await transaction.rollback()

    async with AsyncSession(db_engine) as observer:
        result = await observer.execute(select(User).filter_by(id=STATIC_USER_ID))

    assert result.scalar_one_or_none() is None
