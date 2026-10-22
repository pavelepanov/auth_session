"""Создание таблиц пользователей и сессий."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "180554d1f581"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("admin", "user", native_enum=False, create_constraint=False),
            nullable=False,
        ),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(
        "uq_users_email_lower_btrim",
        "users",
        [sa.text("lower(btrim(email))")],
        unique=True,
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_sessions_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_index("uq_users_email_lower_btrim", table_name="users")
    op.drop_table("users")
