"""Создание ролей и разрешений."""

from typing import Sequence, Union
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision: str = "3c56f8c2e1a4"
down_revision: Union[str, None] = "180554d1f581"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USER_ROLE_ID = UUID("6f29c0b8-8247-4ee8-a91e-9875e61a6b01")
ADMIN_ROLE_ID = UUID("44b0af73-d95e-4bac-852b-c18e5ab24824")
USER_HELLO_WORLD_VIEW_PERMISSION_ID = UUID(
    "9a2e9d33-734a-4227-9776-3debb1a9aeb1"
)
ADMIN_HELLO_WORLD_VIEW_PERMISSION_ID = UUID(
    "8a5a3b50-ce62-481f-95e0-a41f02925c8c"
)


def upgrade() -> None:
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.UUID()),
        sa.column("value", sa.String()),
    )
    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.UUID()),
        sa.column("value", sa.String()),
    )
    roles_permissions_link_table = sa.table(
        "roles_permissions_link",
        sa.column("role_id", sa.UUID()),
        sa.column("permission_id", sa.UUID()),
    )
    op.bulk_insert(
        roles_table,
        [
            {"id": USER_ROLE_ID, "value": "user"},
            {"id": ADMIN_ROLE_ID, "value": "admin"},
        ],
    )
    op.bulk_insert(
        permissions_table,
        [
            {
                "id": USER_HELLO_WORLD_VIEW_PERMISSION_ID,
                "value": "user_hello_world.view",
            },
            {
                "id": ADMIN_HELLO_WORLD_VIEW_PERMISSION_ID,
                "value": "admin_hello_world.view",
            },
        ],
    )
    op.bulk_insert(
        roles_permissions_link_table,
        [
            {
                "role_id": USER_ROLE_ID,
                "permission_id": USER_HELLO_WORLD_VIEW_PERMISSION_ID,
            },
            {
                "role_id": ADMIN_ROLE_ID,
                "permission_id": USER_HELLO_WORLD_VIEW_PERMISSION_ID,
            },
            {
                "role_id": ADMIN_ROLE_ID,
                "permission_id": ADMIN_HELLO_WORLD_VIEW_PERMISSION_ID,
            },
        ],
    )


def downgrade() -> None:
    users_roles_link_table = sa.table(
        "users_roles_link",
        sa.column("role_id", sa.UUID()),
    )
    roles_table = sa.table(
        "roles",
        sa.column("id", sa.UUID()),
    )
    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.UUID()),
    )

    op.execute(
        users_roles_link_table.delete().where(
            users_roles_link_table.c.role_id.in_([USER_ROLE_ID, ADMIN_ROLE_ID])
        )
    )
    op.execute(
        roles_table.delete().where(
            roles_table.c.id.in_([USER_ROLE_ID, ADMIN_ROLE_ID])
        )
    )
    op.execute(
        permissions_table.delete().where(
            permissions_table.c.id.in_(
                [
                    USER_HELLO_WORLD_VIEW_PERMISSION_ID,
                    ADMIN_HELLO_WORLD_VIEW_PERMISSION_ID,
                ]
            )
        )
    )
