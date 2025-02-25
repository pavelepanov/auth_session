from contextlib import asynccontextmanager
from logging import DEBUG, FileHandler, StreamHandler, basicConfig
from typing import Iterable

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import APIRouter, FastAPI
from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext

from auth.entrypoint.config import Config, RabbitMQConfig
from auth.presentation.http.base.error_handler import init_error_handlers
from auth.presentation.http.middlewares.asgi_auth import ASGIAuthMiddleware


def create_app(lifespan: asynccontextmanager) -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    return app


def create_async_ioc_container(
    providers: Iterable[Provider], config: Config, broker: RabbitBroker
) -> AsyncContainer:
    return make_async_container(
        *providers, context={Config: config, RabbitBroker: broker}
    )


def configure_app(app: FastAPI, root_router: APIRouter) -> None:
    app.include_router(root_router)
    app.add_middleware(ASGIAuthMiddleware)
    init_error_handlers(app)


def configure_logging(level=DEBUG):
    format = "[%(asctime)s.%(msecs)03d] %(module)15s:%(lineno)-3d %(levelname)-7s \
     - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = FileHandler("logs.log")
    file_handler.setLevel(level)

    stream_handler = StreamHandler()
    stream_handler.setLevel(level)

    basicConfig(
        level=level,
        datefmt=datefmt,
        format=format,
        handlers=[file_handler, stream_handler],
    )


def create_broker(config: RabbitMQConfig) -> RabbitBroker:
    return RabbitBroker(
        host=config.host,
        port=config.port,
        security=SASLPlaintext(
            username=config.username,
            password=config.password,
        ),
        virtualhost="/",
    )
