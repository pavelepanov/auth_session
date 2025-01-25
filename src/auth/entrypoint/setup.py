from typing import Iterable

from dishka import AsyncContainer, Provider, make_async_container
from fastapi import APIRouter, FastAPI

from auth.entrypoint.config import Config, create_config
from auth.presentation.http.base.error_handler import init_error_handlers
from auth.presentation.http.middlewares.asgi_auth import ASGIAuthMiddleware


def create_app() -> FastAPI:
    app = FastAPI()

    return app


def create_async_ioc_container(providers: Iterable[Provider]) -> AsyncContainer:
    config = create_config()
    return make_async_container(
        *providers,
        context={Config: config},
    )


def configure_app(app: FastAPI, root_router: APIRouter) -> None:
    app.include_router(root_router)
    app.add_middleware(ASGIAuthMiddleware)
    init_error_handlers(app)
