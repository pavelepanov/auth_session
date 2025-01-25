from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from auth.entrypoint.ioc.registry import get_providers
from auth.entrypoint.setup import (configure_app, create_app,
                                   create_async_ioc_container)
from auth.infrastructure.persistence_sqla.mappings.map import map_tables
from auth.presentation.http.base.root_router import root_router


def make_app() -> FastAPI:
    app = create_app()
    map_tables()
    configure_app(app=app, root_router=root_router)

    async_ioc_container: AsyncContainer = create_async_ioc_container(
        providers=(*get_providers(),)
    )

    setup_dishka(container=async_ioc_container, app=app)

    return app
