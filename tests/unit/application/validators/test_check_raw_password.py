import pytest

from auth.application.validators.check_raw_password import check_valid_raw_password
from auth.domain.entities.user import RawPassword


class TestCheckValidRawPassword:

    @pytest.mark.parametrize(
        "password",
        [
            "Password1",
            "Abcdefg1",
            "StrongPass123",
            "MyP4ssword",
            "ABCD1234abcd",
        ],
        ids=[
            "basic_valid",
            "exactly_8_chars",
            "long_with_numbers",
            "digit_in_middle",
            "mixed_case_and_digits",
        ],
    )
    def test_valid_passwords(self, password: str):
        result = check_valid_raw_password(RawPassword(password))
        assert result is True

    @pytest.mark.parametrize(
        "password",
        [
            "short1A",
            "alllowercase1",
            "ALLUPPERCASE1",
            "NoDigitsHere",
            "12345678",
            "",
            "Ab1",
        ],
        ids=[
            "too_short",
            "no_uppercase",
            "no_lowercase",
            "no_digits",
            "only_digits",
            "empty_string",
            "only_3_chars",
        ],
    )
    def test_invalid_passwords(self, password: str):
        result = check_valid_raw_password(RawPassword(password))
        assert result is False
