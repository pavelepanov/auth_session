from enum import StrEnum
from logging import getLogger

logger = getLogger(__name__)


class UserRoleEnum(StrEnum):
    ADMIN = "admin"
    USER = "user"


def has_required_role(user_role: UserRoleEnum, required_role: UserRoleEnum) -> bool:
    if required_role is UserRoleEnum.USER:
        return user_role in {UserRoleEnum.USER, UserRoleEnum.ADMIN}

    if required_role is UserRoleEnum.ADMIN:
        return user_role is UserRoleEnum.ADMIN
