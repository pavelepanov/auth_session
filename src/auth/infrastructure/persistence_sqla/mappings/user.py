from sqlalchemy import UUID, Boolean, Column, String, Table

from auth.domain.entities.user import User
from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry

users_table = Table(
    "users",
    mapping_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("username", String, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("is_active", Boolean, nullable=False),
)


def map_users_table() -> None:
    mapping_registry.map_imperatively(
        User,
        users_table,
    )
