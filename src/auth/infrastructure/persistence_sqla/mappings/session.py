from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Table

from auth.domain.entities.session import Session
from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry

sessions_table = Table(
    "sessions",
    mapping_registry.metadata,
    Column("id", String, primary_key=True),
    Column("expiration", DateTime(timezone=True), nullable=False),
    Column("user_id", UUID, ForeignKey("users.id"), unique=True),
)


def map_sessions_table() -> None:
    mapping_registry.map_imperatively(
        Session,
        sessions_table,
    )
