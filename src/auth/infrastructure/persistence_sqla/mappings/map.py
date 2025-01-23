from auth.infrastructure.persistence_sqla.mappings.user import map_users_table


def map_tables() -> None:
    map_users_table()
