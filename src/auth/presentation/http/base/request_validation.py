from typing import Any

from auth.application.errors import ErrorDetail

_VALIDATION_MESSAGES: dict[str, tuple[str, str]] = {
    "missing": ("REQUIRED_FIELD", "Обязательное поле."),
    "string_type": ("INVALID_TYPE", "Ожидается строка."),
    "string_unicode": ("INVALID_UNICODE", "Недопустимые символы Unicode."),
    "string_too_short": ("INVALID_LENGTH", "Слишком короткое значение."),
    "string_too_long": ("INVALID_LENGTH", "Слишком длинное значение."),
    "json_invalid": ("INVALID_JSON", "Некорректный JSON."),
    "json_type": ("INVALID_JSON", "Некорректный JSON."),
    "model_attributes_type": ("INVALID_TYPE", "Ожидается объект."),
    "model_type": ("INVALID_TYPE", "Ожидается объект."),
    "dict_type": ("INVALID_TYPE", "Ожидается объект."),
    "extra_forbidden": ("UNEXPECTED_FIELD", "Неизвестное поле."),
}


def get_validation_details(errors: list[Any]) -> list[ErrorDetail]:
    """Не передаёт клиенту input, msg и ctx: они могут содержать секреты."""
    details = []
    for error in errors:
        location = error.get("loc", ())
        error_type = error.get("type", "")
        if error_type == "json_invalid":
            field = "body"
        else:
            parts = location
            if parts and parts[0] in {"body", "query", "path", "header", "cookie"}:
                parts = parts[1:]
            field = ".".join(str(part) for part in parts) or "body"

        if error_type == "value_error" and location and location[-1] == "email":
            code, message = "INVALID_EMAIL", "Некорректный email."
        else:
            code, message = _VALIDATION_MESSAGES.get(
                error_type, ("INVALID_VALUE", "Некорректное значение.")
            )
        details.append(ErrorDetail(field=field, code=code, message=message))
    return details
