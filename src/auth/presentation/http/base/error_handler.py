from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.utils import is_body_allowed_for_status_code
from starlette.exceptions import HTTPException

from auth.application.errors import ApplicationError
from auth.presentation.http.base.error_response import (
    BAD_REQUEST_CODE,
    BAD_REQUEST_MESSAGE,
    INTERNAL_ERROR_CODE,
    INTERNAL_ERROR_MESSAGE,
    VALIDATION_ERROR_CODE,
    VALIDATION_ERROR_MESSAGE,
    create_error_response,
)
from auth.presentation.http.base.error_status_codes import get_error_http_status
from auth.presentation.http.base.request_validation import get_validation_details

_HTTP_ERRORS: dict[int, tuple[str, str]] = {
    400: (BAD_REQUEST_CODE, BAD_REQUEST_MESSAGE),
    401: ("UNAUTHENTICATED", "Пользователь не авторизован."),
    403: ("PERMISSION_DENIED", "Недостаточно прав."),
    404: ("NOT_FOUND", "Ресурс не найден."),
    405: ("METHOD_NOT_ALLOWED", "Метод запроса не поддерживается."),
    415: ("UNSUPPORTED_MEDIA_TYPE", "Неподдерживаемый тип содержимого."),
    422: (VALIDATION_ERROR_CODE, VALIDATION_ERROR_MESSAGE),
    429: ("TOO_MANY_REQUESTS", "Слишком много запросов."),
}


async def application_error_handler(_: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, ApplicationError):
        raise error
    status = get_error_http_status(type(error))
    if status == 500:
        return await unexpected_error_handler(_, error)
    return JSONResponse(
        status_code=status,
        content=create_error_response(error.code, error.message, error.details),
    )


async def request_validation_error_handler(
    _: Request, error: Exception
) -> JSONResponse:
    if not isinstance(error, RequestValidationError):
        raise error
    return JSONResponse(
        status_code=422,
        content=create_error_response(
            VALIDATION_ERROR_CODE,
            VALIDATION_ERROR_MESSAGE,
            get_validation_details(error.errors()),
        ),
    )


async def http_error_handler(_: Request, error: Exception) -> Response:
    if not isinstance(error, HTTPException):
        raise error
    if not is_body_allowed_for_status_code(error.status_code):
        return Response(status_code=error.status_code, headers=error.headers)
    if error.status_code >= 500:
        code, message = INTERNAL_ERROR_CODE, INTERNAL_ERROR_MESSAGE
    else:
        code, message = _HTTP_ERRORS.get(
            error.status_code, ("HTTP_ERROR", "Ошибка HTTP-запроса.")
        )
    return JSONResponse(
        status_code=error.status_code,
        content=create_error_response(code, message),
        headers=error.headers,
    )


async def unexpected_error_handler(_: Request, error: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=create_error_response(INTERNAL_ERROR_CODE, INTERNAL_ERROR_MESSAGE),
    )


def init_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
