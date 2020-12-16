import pytest

from chocs.json_schema.errors import MaximumLengthError
from chocs.json_schema.errors import MinimumLengthError
from chocs.json_schema.errors import UniqueValidationError
from chocs.json_schema.validators import validate_integer
from chocs.json_schema.validators import validate_items
from chocs.json_schema.validators import validate_maximum_items
from chocs.json_schema.validators import validate_minimum_items
from chocs.json_schema.validators import validate_unique


def test_pass_validate_unique() -> None:
    assert validate_unique([1, 2, 3, 4, "true", True])


def test_fail_validate_unique() -> None:
    with pytest.raises(UniqueValidationError):
        validate_unique([1, 1])


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
