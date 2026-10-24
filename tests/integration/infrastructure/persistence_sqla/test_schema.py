from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncConnection

from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry


async def test_migrated_schema_matches_mappings(db_connection: AsyncConnection) -> None:
    """Catch mapping changes that need a migration, even for unused columns."""

    def differences(connection: Connection) -> list[object]:
        context = MigrationContext.configure(
            connection, opts={"compare_type": True, "compare_server_default": True}
        )
        return list(compare_metadata(context, mapping_registry.metadata))

    changes = await db_connection.run_sync(differences)

    assert changes == [], f"Mappings and migrations differ: {changes!r}"
