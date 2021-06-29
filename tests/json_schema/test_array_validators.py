import pytest

from chocs.json_schema.errors import (
    MaximumLengthError,
    MinimumLengthError,
    UniqueItemsValidationError,
)
from chocs.json_schema.validators import (
    validate_integer,
    validate_items,
    validate_maximum_items,
    validate_minimum_items,
    validate_unique_items,
)


def test_pass_validate_unique() -> None:
    assert validate_unique_items([1, 2, 3, 4, "true", True])


def test_fail_validate_unique() -> None:
    with pytest.raises(UniqueItemsValidationError):
        validate_unique_items([1, 1])


def test_pass_validate_minimum_items() -> None:
    assert validate_minimum_items([1], 1)
    assert validate_minimum_items([1, 2], 1)


def test_fail_validate_minimum_items() -> None:
    with pytest.raises(MinimumLengthError):
        assert validate_minimum_items([1], 2)


def test_pass_validate_maximum_items() -> None:
    assert validate_maximum_items([1], 1)
    assert validate_maximum_items([1, 2], 3)


def test_fail_validate_maximum_items() -> None:
    with pytest.raises(MaximumLengthError):
        assert validate_maximum_items([1, 2], 1)


def test_pass_validate_items() -> None:
    assert validate_items([1, 2, 3], validate_integer)


def test_fail_validate_items() -> None:
    with pytest.raises(ValueError):
        validate_items([1, 2.1, 3], validate_integer)
