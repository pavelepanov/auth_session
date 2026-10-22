from functools import partial
from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status as code

from auth.application.errors import (
    AlreadyExists,
    AuthenticationError,
    DoesNotExists,
    InvalidPassword,
    LogInError,
    LogOutError,
    SignUpError,
)
from auth.domain.errors import AccessControlError, Error


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
        SignUpError, partial(validate, status=code.HTTP_409_CONFLICT)
    )
    app.add_exception_handler(
        LogInError, partial(validate, status=code.HTTP_409_CONFLICT)
    )
    app.add_exception_handler(
        LogOutError, partial(validate, status=code.HTTP_409_CONFLICT)
    )
    app.add_exception_handler(
        AccessControlError, partial(validate, status=code.HTTP_403_FORBIDDEN)
    )
