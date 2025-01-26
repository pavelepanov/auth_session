from auth.application.constants import raw_password_pattern
from auth.domain.entities.user import RawPassword


def check_valid_raw_password(raw_password: RawPassword) -> bool:
    return bool(raw_password_pattern.match(raw_password))
