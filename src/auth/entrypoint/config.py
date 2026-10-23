from dataclasses import dataclass
from os import environ, getenv
from urllib.parse import quote


@dataclass
class SessionConfig:
    expiration_minutes: int
    token_hash_secret: str
    cookie_name: str = "__Host-session"
    cookie_secure: bool = True
    cookie_samesite: str = "lax"

    @staticmethod
    def from_env() -> SessionConfig:
        expiration_minutes = environ["SESSION_EXPIRATION_MINUTES"]
        token_hash_secret = environ["SESSION_TOKEN_HASH_SECRET"]
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
    def from_env() -> PostgresConfig:
        host = environ["POSTGRES_HOST"]
        port = int(environ["POSTGRES_PORT"])
        db = environ["POSTGRES_DB"]
        user = environ["POSTGRES_USER"]
        password = environ["POSTGRES_PASS"]

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
