from functools import partial
from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status as code

from auth.application.errors import (
    AlreadyAuthenticated,
    AlreadyExists,
    AuthenticationError,
    DoesNotExists,
    InvalidPassword,
)
from auth.domain.errors import Error


class HTTPError(Error): ...


async def validate(_: Request, error: Exception, status: int) -> JSONResponse:
    error = cast(HTTPError, error)
    return JSONResponse(content={"message": error.message}, status_code=status)


def init_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AuthenticationError,
        partial(validate, status=code.HTTP_401_UNAUTHORIZED),
    )
    app.add_exception_handler(
        InvalidPassword,
        partial(validate, status=code.HTTP_400_BAD_REQUEST),
    )
    app.add_exception_handler(
        AlreadyExists,
        partial(validate, status=code.HTTP_409_CONFLICT),
    )
    app.add_exception_handler(
        DoesNotExists,
        partial(validate, status=code.HTTP_404_NOT_FOUND),
    )
    app.add_exception_handler(
        AlreadyAuthenticated, partial(validate, status=code.HTTP_409_CONFLICT)
    )
