from collections.abc import Iterable
from logging import INFO, StreamHandler, basicConfig

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import APIRouter, FastAPI
from starlette.types import Lifespan

from auth.entrypoint.config import Config
from auth.presentation.http.base.error_handler import init_error_handlers
from auth.presentation.http.middlewares.asgi_auth import ASGIAuthMiddleware


def create_app(lifespan: Lifespan[FastAPI]) -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    return app


def create_async_ioc_container(
    providers: Iterable[Provider], config: Config
) -> AsyncContainer:
    return make_async_container(*providers, context={Config: config})


def configure_app(app: FastAPI, root_router: APIRouter) -> None:
    app.include_router(root_router)
    app.add_middleware(ASGIAuthMiddleware)
    init_error_handlers(app)


def configure_logging(level: int = INFO) -> None:
    format = "[%(asctime)s.%(msecs)03d] %(module)15s:%(lineno)-3d %(levelname)-7s \
     - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    stream_handler = StreamHandler()
    stream_handler.setLevel(level)

    basicConfig(
        level=level,
        datefmt=datefmt,
        format=format,
        handlers=[stream_handler],
    )
