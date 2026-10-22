from dataclasses import dataclass
from os import getenv
from urllib.parse import quote


@dataclass
class SessionConfig:
    expiration_minutes: int
    token_hash_secret: str
    cookie_name: str = "__Host-session"
    cookie_secure: bool = True
    cookie_samesite: str = "lax"

    @staticmethod
    def from_env() -> "SessionConfig":
        expiration_minutes = getenv("SESSION_EXPIRATION_MINUTES")
        token_hash_secret = getenv("SESSION_TOKEN_HASH_SECRET")
        cookie_name = getenv("SESSION_COOKIE_NAME", "__Host-session")
        cookie_secure = getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
        cookie_samesite = getenv("SESSION_COOKIE_SAMESITE", "lax")

        return SessionConfig(
            expiration_minutes=int(expiration_minutes),
            token_hash_secret=token_hash_secret,
            cookie_name=cookie_name,
            cookie_secure=cookie_secure,
            cookie_samesite=cookie_samesite,
        )


@dataclass
class PostgresConfig:
    host: str
    port: int
    db: str
    user: str
    password: str

    uri: str

    @staticmethod
    def from_env() -> "PostgresConfig":
        host = getenv("POSTGRES_HOST")
        port = getenv("POSTGRES_PORT")
        db = getenv("POSTGRES_DB")
        user = getenv("POSTGRES_USER")
        password = getenv("POSTGRES_PASS")

        uri = (
            f"postgresql+psycopg://"
            f"{quote(user, safe='')}:{quote(password, safe='')}@{host}:{port}/{db}"
        )

        return PostgresConfig(
            uri=uri, host=host, port=port, db=db, user=user, password=password
        )


@dataclass
class Config:
    postgres_config: PostgresConfig
    session_config: SessionConfig


def create_config() -> Config:
    return Config(
        postgres_config=PostgresConfig.from_env(),
        session_config=SessionConfig.from_env(),
    )
