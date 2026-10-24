from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.session import Session, SessionId, SessionTokenHash
from auth.domain.entities.user import User, UserId
from auth.infrastructure.adapters.session_data_mapper_sqla import SessionDataMapperSqla
from tests.conftest import STATIC_TOKEN_HASH


@pytest.fixture
async def stored_session(
    db_session: AsyncSession,
    sample_user: User,
    sample_session: Session,
    session_gateway: SessionDataMapperSqla,
) -> Session:
    db_session.add(sample_user)
    await db_session.flush()
    await session_gateway.add(sample_session)
    await db_session.flush()
    return sample_session


async def test_round_trip_preserves_utc_timestamps(
    db_session: AsyncSession,
    session_gateway: SessionDataMapperSqla,
    stored_session: Session,
) -> None:
    db_session.expunge_all()

    found = await session_gateway.read_by_token_hash(stored_session.token_hash)

    assert found is not None
    assert found.id == stored_session.id
    assert found.user_id == stored_session.user_id
    assert found.token_hash == STATIC_TOKEN_HASH
    assert found.expires_at == stored_session.expires_at
    assert found.created_at == stored_session.created_at
    assert found.expires_at.utcoffset() == timedelta(0)


async def test_prolongation_is_persisted(
    db_session: AsyncSession,
    session_gateway: SessionDataMapperSqla,
    stored_session: Session,
) -> None:
    expires_at = stored_session.expires_at + timedelta(minutes=30)

    await session_gateway.prolong(stored_session, expires_at)
    await db_session.commit()
    db_session.expunge_all()
    found = await session_gateway.read_by_token_hash(stored_session.token_hash)

    assert found is not None
    assert found.expires_at == expires_at


async def test_deletion_is_persisted(
    db_session: AsyncSession,
    session_gateway: SessionDataMapperSqla,
    stored_session: Session,
) -> None:
    await session_gateway.delete(stored_session)
    await db_session.commit()

    assert await session_gateway.read_by_token_hash(stored_session.token_hash) is None


async def test_user_can_have_independent_sessions(
    db_session: AsyncSession,
    session_gateway: SessionDataMapperSqla,
    stored_session: Session,
) -> None:
    second = Session(
        id=SessionId(uuid4()),
        token_hash=SessionTokenHash("b" * 64),
        user_id=stored_session.user_id,
        created_at=stored_session.created_at,
        expires_at=stored_session.expires_at,
    )
    await session_gateway.add(second)
    await db_session.commit()

    await session_gateway.delete(stored_session)
    await db_session.commit()

    assert await session_gateway.read_by_token_hash(second.token_hash) == second
    assert await session_gateway.read_by_token_hash(stored_session.token_hash) is None


async def test_user_deletion_cascades_to_sessions(
    db_session: AsyncSession,
    sample_user: User,
    session_gateway: SessionDataMapperSqla,
    stored_session: Session,
) -> None:
    await db_session.delete(sample_user)
    await db_session.commit()
    db_session.expunge_all()

    assert await session_gateway.read_by_token_hash(stored_session.token_hash) is None


async def test_missing_token_is_absent(session_gateway: SessionDataMapperSqla) -> None:
    assert await session_gateway.read_by_token_hash(STATIC_TOKEN_HASH) is None


async def test_session_requires_existing_user(
    db_session: AsyncSession,
    session_gateway: SessionDataMapperSqla,
    sample_session: Session,
) -> None:
    sample_session.user_id = UserId(uuid4())
    await session_gateway.add(sample_session)

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_token_hash_must_be_unique(
    db_session: AsyncSession,
    session_gateway: SessionDataMapperSqla,
    stored_session: Session,
) -> None:
    duplicate = Session(
        id=SessionId(uuid4()),
        token_hash=stored_session.token_hash,
        user_id=stored_session.user_id,
        created_at=stored_session.created_at,
        expires_at=stored_session.expires_at,
    )
    await session_gateway.add(duplicate)

    with pytest.raises(IntegrityError):
        await db_session.flush()
