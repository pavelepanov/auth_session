from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel

from auth.application.errors import ApplicationError, ErrorDetail
from auth.presentation.http.base.error_status_codes import (
    ERROR_HTTP_STATUSES,
    get_error_http_status,
)

INTERNAL_ERROR_CODE = "INTERNAL_ERROR"
INTERNAL_ERROR_MESSAGE = "Внутренняя ошибка сервера."
BAD_REQUEST_CODE = "BAD_REQUEST"
BAD_REQUEST_MESSAGE = "Некорректный запрос."
VALIDATION_ERROR_CODE = "REQUEST_VALIDATION_ERROR"
VALIDATION_ERROR_MESSAGE = "Некорректные данные запроса."


class ErrorDataModel(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponseModel(BaseModel):
    error: ErrorDataModel


def create_error_response(
    code: str,
    message: str,
    details: Iterable[ErrorDetail] = (),
) -> dict[str, Any]:
    items = list(details)
    return ErrorResponseModel(
        error=ErrorDataModel(code=code, message=message, details=items or None)
    ).model_dump(mode="json", exclude_none=True)


def get_error_responses(
    *error_types: type[ApplicationError],
    include_validation: bool = False,
) -> dict[int | str, dict[str, Any]]:
    """Объединяет ошибки одного HTTP-статуса, сохраняя все примеры для Swagger."""
    responses: dict[int | str, dict[str, Any]] = {}

    def add_response(
        status_code: int,
        code: str,
        message: str,
        details: Iterable[ErrorDetail] = (),
    ) -> None:
        response = responses.setdefault(
            status_code,
            {
                "model": ErrorResponseModel,
                "description": "",
                "content": {"application/json": {"examples": {}}},
            },
        )
        examples = response["content"]["application/json"]["examples"]
        examples[code] = {
            "summary": message,
            "value": create_error_response(code, message, details),
        }
        response["description"] = "\n\n".join(
            f"`{key}` — {value['summary']}" for key, value in examples.items()
        )

    for error_type in error_types:
        if error_type not in ERROR_HTTP_STATUSES:
            raise ValueError(f"HTTP status is not registered for {error_type.__name__}")
        add_response(
            get_error_http_status(error_type), error_type.code, error_type.message
        )

    if include_validation:
        add_response(400, BAD_REQUEST_CODE, BAD_REQUEST_MESSAGE)
        add_response(
            422,
            VALIDATION_ERROR_CODE,
            VALIDATION_ERROR_MESSAGE,
            [
                ErrorDetail(
                    field="body", code="INVALID_JSON", message="Некорректный JSON."
                )
            ],
        )
    add_response(500, INTERNAL_ERROR_CODE, INTERNAL_ERROR_MESSAGE)
    return responses
