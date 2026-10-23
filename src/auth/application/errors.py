from collections.abc import Iterable
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ErrorDetail:
    """Детали передаются клиенту; пароли и токены сюда не включать."""

    field: str
    code: str
    message: str


class ApplicationError(Exception):
    code: ClassVar[str] = "APPLICATION_ERROR"
    message: str = "Ошибка приложения."
    details: tuple[ErrorDetail, ...] = ()

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Iterable[ErrorDetail] | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        self.details = tuple(details) if details is not None else self.details
        super().__init__(self.message)


class UnauthenticatedError(ApplicationError):
    code = "UNAUTHENTICATED"
    message = "Пользователь не аутентифицирован."


class InvalidCredentialsError(ApplicationError):
    code = "INVALID_CREDENTIALS"
    message = "Неверный email или пароль."


class AlreadyAuthenticatedError(ApplicationError):
    code = "ALREADY_AUTHENTICATED"
    message = "Вы уже авторизованы."


class PermissionDeniedError(ApplicationError):
    code = "PERMISSION_DENIED"
    message = "Недостаточно прав."


class UserEmailAlreadyExistsError(ApplicationError):
    code = "USER_EMAIL_ALREADY_EXISTS"
    message = "Пользователь с таким email уже существует."


class InvalidPasswordError(ApplicationError):
    code = "INVALID_PASSWORD"
    message = "Пароль не соответствует требованиям."
