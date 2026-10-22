from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Index,
    String,
    Table,
    func,
)
from sqlalchemy.orm import relationship

from auth.domain.entities.user import (
    Permission,
    PermissionEnum,
    Role,
    User,
    UserRoleEnum,
)
from auth.infrastructure.persistence_sqla.orm_registry import mapping_registry

users_table = Table(
    "users",
    mapping_registry.metadata,
    Column("id", UUID, primary_key=True),
    Column("email", String, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("is_active", Boolean, nullable=False),
)

roles_table = Table(
    "roles",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "value",
        Enum(
            UserRoleEnum,
            name="user_role",
            length=64,
            native_enum=False,
            create_constraint=False,
            values_callable=lambda roles: [role.value for role in roles],
        ),
        nullable=False,
        unique=True,
    ),
)

permissions_table = Table(
    "permissions",
    mapping_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "value",
        Enum(
            PermissionEnum,
            name="permission",
            length=64,
            native_enum=False,
            create_constraint=False,
            values_callable=lambda permissions: [
                permission.value for permission in permissions
            ],
        ),
        nullable=False,
        unique=True,
    ),
)

users_roles_link_table = Table(
    "users_roles_link",
    mapping_registry.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)

roles_permissions_link_table = Table(
    "roles_permissions_link",
    mapping_registry.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

Index(
    "uq_users_email_lower_btrim",
    func.lower(func.btrim(users_table.c.email)),
    unique=True,
)


def map_users_table() -> None:
    mapping_registry.map_imperatively(
        Permission,
        permissions_table,
    )
    mapping_registry.map_imperatively(
        Role,
        roles_table,
        properties={
            "permissions": relationship(
                Permission,
                secondary=roles_permissions_link_table,
                lazy="selectin",
            ),
        },
    )
    mapping_registry.map_imperatively(
        User,
        users_table,
        properties={
            "roles": relationship(
                Role,
                secondary=users_roles_link_table,
                lazy="selectin",
            ),
        },
    )
