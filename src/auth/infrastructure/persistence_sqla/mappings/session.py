from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Table

from auth.domain.entities.session import Session
from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry

sessions_table = Table(
    "sessions",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("token_hash", String, nullable=False, unique=True),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


def map_sessions_table() -> None:
    mapping_registry.map_imperatively(
        Session,
        sessions_table,
    )
