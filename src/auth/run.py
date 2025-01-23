from fastapi import FastAPI

from auth.entrypoint.setup import create_app


def make_app() -> FastAPI:
    app = create_app()

    return app
