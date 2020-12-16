from chocs.json_schema import StringFormat
from chocs.json_schema.validators import validate_string_format
import pytest


def test_can_define_new_format() -> None:
    def my_format_validator(value: str) -> str:
        if value == "valid value":
            return value

        raise ValueError()

    with pytest.raises(KeyError):
        validate_string_format("valid value", "my-format")

    StringFormat['my-format'] = my_format_validator

    assert validate_string_format("valid value", "my-format")

    with pytest.raises(ValueError):
        validate_string_format("invalid", "my-format")


def test_can_use_predefined_format() -> None:
    assert validate_string_format("email@test.com", "email")


def test_format_exists() -> None:
    assert "new-format" not in StringFormat
    assert "ip-address" in StringFormat
