from collections.abc import Mapping
from types import MappingProxyType

from starlette import status

from auth.application.errors import (
    AlreadyAuthenticatedError,
    ApplicationError,
    InvalidCredentialsError,
    InvalidPasswordError,
    PermissionDeniedError,
    UnauthenticatedError,
    UserEmailAlreadyExistsError,
)

ERROR_HTTP_STATUSES: Mapping[type[ApplicationError], int] = MappingProxyType(
    {
        UnauthenticatedError: status.HTTP_401_UNAUTHORIZED,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        AlreadyAuthenticatedError: status.HTTP_409_CONFLICT,
        PermissionDeniedError: status.HTTP_403_FORBIDDEN,
        UserEmailAlreadyExistsError: status.HTTP_409_CONFLICT,
        InvalidPasswordError: status.HTTP_400_BAD_REQUEST,
    }
)


def get_error_http_status(error_type: type[ApplicationError]) -> int:
    # Отсутствие статуса в таблице — ошибка настройки сервера, поэтому возвращаем 500.
    return ERROR_HTTP_STATUSES.get(error_type, status.HTTP_500_INTERNAL_SERVER_ERROR)
