import pytest

from chocs.json_schema.errors import FormatValidationError, MaximumLengthError, MinimumLengthError
from chocs.json_schema.validators import validate_maximum_length, validate_minimum_length, validate_string_pattern


@pytest.mark.parametrize(
    "value, pattern", [["test", "^t[a-z]+"], ["123", "[0-3]+"], ["a23bcd", "[a-d2-3]+"]]
)
def test_pass_validate_string_pattern(value: str, pattern: str) -> None:
    assert validate_string_pattern(value, pattern)


@pytest.mark.parametrize("value, pattern", [["atest", "^t[a-z]+"], ["124", "[a-z]"],])
def test_fail_validate_string_pattern(value: str, pattern: str) -> None:
    with pytest.raises(FormatValidationError):
        validate_string_pattern(value, pattern)


@pytest.mark.parametrize(
    "value, expected_minimum", [["test", 1], ["123", 3], ["a23bcd", 0]]
)
def test_pass_validate_minimum_length(value: str, expected_minimum: int) -> None:
    assert validate_minimum_length(value, expected_minimum)


@pytest.mark.parametrize("value, expected_minimum", [["test", 5], ["123", 10],])
def test_fail_validate_minimum_length(value: str, expected_minimum: int) -> None:
    with pytest.raises(MinimumLengthError):
        validate_minimum_length(value, expected_minimum)


@pytest.mark.parametrize(
    "value, expected_maximum", [["test", 4], ["123", 3], ["a23bcd", 10]]
)
def test_pass_validate_maximum_length(value: str, expected_maximum: int) -> None:
    assert validate_maximum_length(value, expected_maximum)


@pytest.mark.parametrize("value, expected_maximum", [["test", 3], ["123", 1],])
def test_fail_validate_maximum_length(value: str, expected_maximum: int) -> None:
    with pytest.raises(MaximumLengthError):
        validate_maximum_length(value, expected_maximum)
