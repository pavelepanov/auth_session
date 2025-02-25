from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class SessionConfig:
    expiration_minutes: int

    @staticmethod
    def from_env() -> "SessionConfig":
        expiration_minutes = getenv("SESSION_EXPIRATION_MINUTES")

        return SessionConfig(expiration_minutes=int(expiration_minutes))


@dataclass
class RedisConfig:
    host: str
    port: int
    ttl: int

    @staticmethod
    def from_env() -> "RedisConfig":
        host = getenv("REDIS_HOST")
        port = getenv("REDIS_PORT")
        ttl = getenv("REDIS_TTL")

        return RedisConfig(
            host=host,
            port=port,
            ttl=int(ttl),
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

        uri = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

        return PostgresConfig(
            uri=uri, host=host, port=port, db=db, user=user, password=password
        )


@dataclass
class RabbitMQConfig:
    host: str
    port: int
    username: str
    password: str

    email_sender_queue: str

    @staticmethod
    def from_env() -> "RabbitMQConfig":
        host = getenv("RABBITMQ_HOST")
        port = getenv("RABBITMQ_PORT")
        username = getenv("RABBITMQ_USERNAME")
        password = getenv("RABBITMQ_PASSWORD")
        email_sender_queue = getenv("RABBITMQ_EMAIL_SENDER_QUEUE")

        return RabbitMQConfig(
            host=host,
            port=int(port),
            username=username,
            password=password,
            email_sender_queue=email_sender_queue,
        )


@dataclass
class Config:
    redis_config: RedisConfig
    postgres_config: PostgresConfig
    session_config: SessionConfig
    rabbitmq_config: RabbitMQConfig


def create_config() -> Config:
    return Config(
        redis_config=RedisConfig.from_env(),
        postgres_config=PostgresConfig.from_env(),
        session_config=SessionConfig.from_env(),
        rabbitmq_config=RabbitMQConfig.from_env(),
    )
