from auth.application.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from auth.domain.entities.user import RawPassword


def check_valid_raw_password(raw_password: RawPassword) -> bool:
    if not MIN_PASSWORD_LENGTH <= len(raw_password) <= MAX_PASSWORD_LENGTH:
        return False

    try:
        raw_password.encode("utf-8")
    except UnicodeEncodeError:
        return False

    return True
