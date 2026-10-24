import pytest

from auth.application.validators.check_raw_password import check_valid_raw_password
from auth.domain.entities.user import RawPassword


class TestCheckValidRawPassword:
    @pytest.mark.parametrize(
        ("password", "expected"),
        [
            pytest.param("", False, id="empty"),
            pytest.param("a" * 14, False, id="below_minimum"),
            pytest.param("a" * 15, True, id="minimum"),
            pytest.param("a" * 128, True, id="maximum"),
            pytest.param("a" * 129, False, id="above_maximum"),
            pytest.param("пароль" * 3, True, id="unicode"),
            pytest.param("😀" * 15, True, id="multibyte_characters"),
            pytest.param("a" * 15 + "\ud800", False, id="invalid_unicode"),
        ],
    )
    def test_password_requirements(self, password: str, expected: bool) -> None:
        result = check_valid_raw_password(RawPassword(password))

        assert result is expected
