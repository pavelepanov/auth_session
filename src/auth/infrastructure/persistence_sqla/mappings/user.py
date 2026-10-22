from sqlalchemy import UUID, Boolean, Column, Enum, Index, String, Table, func

from auth.domain.entities.user import User
from auth.domain.user_role import UserRoleEnum
from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry

users_table = Table(
    "users",
    mapping_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("email", String, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column(
        "role",
        Enum(
            UserRoleEnum,
            native_enum=False,
            create_constraint=False,
            values_callable=lambda roles: [role.value for role in roles],
        ),
        nullable=False,
    ),
    Column("is_verified", Boolean, nullable=False),
)

Index(
    "uq_users_email_lower_btrim",
    func.lower(func.btrim(users_table.c.email)),
    unique=True,
)


def map_users_table() -> None:
    mapping_registry.map_imperatively(
        User,
        users_table,
    )
