from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.user import User, UserEmail, UserId
from auth.infrastructure.adapters.user_data_mapper_sqla import UserDataMapperSqla


async def test_user_round_trip_includes_roles_and_permissions(
    db_session: AsyncSession,
    user_gateway: UserDataMapperSqla,
    sample_user: User,
) -> None:
    await user_gateway.add(sample_user)
    await db_session.flush()
    db_session.expunge_all()

    found = await user_gateway.read_by_id(sample_user.id)

    assert found is not None
    assert found.email == sample_user.email
    assert found.password_hash == sample_user.password_hash
    assert found.is_active is True
    assert found.roles[0].value == "user"
    assert [permission.value for permission in found.roles[0].permissions] == [
        "user_hello_world.view"
    ]


@pytest.mark.parametrize("email", ["test@example.com", " TEST@EXAMPLE.COM "])
async def test_email_lookup_is_case_and_space_insensitive(
    db_session: AsyncSession,
    user_gateway: UserDataMapperSqla,
    sample_user: User,
    email: str,
) -> None:
    sample_user.email = UserEmail(" Test@Example.COM ")
    await user_gateway.add(sample_user)
    await db_session.flush()
    db_session.expunge_all()

    found = await user_gateway.read_by_email(UserEmail(email))

    assert found is not None
    assert found.id == sample_user.id


async def test_unknown_user_is_absent(user_gateway: UserDataMapperSqla) -> None:
    assert await user_gateway.read_by_id(UserId(uuid4())) is None
    assert await user_gateway.read_by_email(UserEmail("absent@example.com")) is None


async def test_duplicate_normalized_email_is_rejected(
    db_session: AsyncSession,
    user_gateway: UserDataMapperSqla,
    sample_user: User,
) -> None:
    await user_gateway.add(sample_user)
    await db_session.flush()
    duplicate = User(
        id=UserId(uuid4()),
        email=UserEmail(" TEST@EXAMPLE.COM "),
        password_hash=sample_user.password_hash,
        is_active=True,
    )
    await user_gateway.add(duplicate)

    with pytest.raises(IntegrityError):
        await db_session.flush()

    await db_session.rollback()
    assert await user_gateway.read_by_email(sample_user.email) is None
