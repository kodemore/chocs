from decimal import Decimal
from numbers import Number
from typing import Union

import pytest

from chocs.json_schema.errors import MaximumExclusiveRangeError
from chocs.json_schema.errors import MaximumRangeError
from chocs.json_schema.errors import MinimumExclusiveRangeError
from chocs.json_schema.errors import MinimumRangeError
from chocs.json_schema.errors import MultipleOfValidationError
from chocs.json_schema.validators import validate_exclusive_maximum
from chocs.json_schema.validators import validate_exclusive_minimum
from chocs.json_schema.validators import validate_maximum
from chocs.json_schema.validators import validate_minimum
from chocs.json_schema.validators import validate_multiple_of


@pytest.mark.parametrize("value, expected_minimum", [
    [1, 1],
    [2, 1],
    [1.1, 1],
    [1.1, 1.1],
])
def test_pass_validate_minimum(value: int, expected_minimum: int) -> None:
    assert validate_minimum(value, expected_minimum)


@pytest.mark.parametrize("value, expected_minimum", [
    [0, 1],
    [1, 3],
    [1.1, 2]
])
def test_fail_validate_minimum(value: int, expected_minimum: int) -> None:
    with pytest.raises(MinimumRangeError):
        validate_minimum(value, expected_minimum)


@pytest.mark.parametrize("value, expected_maximum", [
    [1, 1],
    [1, 2],
    [1.1, 1.1],
    [1, 2.1],
])
def test_pass_validate_maximum(value: int, expected_maximum: int) -> None:
    assert validate_maximum(value, expected_maximum)


@pytest.mark.parametrize("value, expected_maximum", [
    [2, 1],
    [2.1, 2],
    [1.2, 1.1],
    [1, 0.9],
])
def test_fail_validate_maximum(value: int, expected_maximum: int) -> None:
    with pytest.raises(MaximumRangeError):
        validate_maximum(value, expected_maximum)


@pytest.mark.parametrize("value, expected_maximum", [
    [1, 2],
    [1.1, 1.2],
    [1, 2.1],
    [1.1, 2.1],
])
def test_pass_validate_exclusive_maximum(value: int, expected_maximum: int) -> None:
    assert validate_exclusive_maximum(value, expected_maximum)


@pytest.mark.parametrize("value, expected_maximum", [
    [1, 1],
    [1.1, 1.1],
    [1.1, 1],
    [1, 0.9],
])
def test_fail_validate_exclusive_maximum(value: int, expected_maximum: int) -> None:
    with pytest.raises(MaximumExclusiveRangeError):
        validate_exclusive_maximum(value, expected_maximum)


@pytest.mark.parametrize("value, expected_minimum", [
    [2, 1],
    [1.2, 1.1],
    [2, 1.9],
])
def test_pass_validate_exclusive_minimum(value: int, expected_minimum: int) -> None:
    assert validate_exclusive_minimum(value, expected_minimum)


@pytest.mark.parametrize("value, expected_minimum", [
    [1, 1],
    [1.1, 1.2],
    [1, 1.1],
    [1.9, 2],
])
def test_fail_validate_exclusive_minimum(value: int, expected_minimum: int) -> None:
    with pytest.raises(MinimumExclusiveRangeError):
        validate_exclusive_minimum(value, expected_minimum)


@pytest.mark.parametrize("value, multiple_of", [
    [2, 2],
    [2, 1],
    [9, 3],
    [Decimal("4"), Decimal("2")],
    [Decimal("4"), 2],
    [4.0, 2],
    [4.4, 2.2],
])
def test_pass_validate_multiple_of(value: Union[int, float, Decimal], multiple_of: Union[int, float, Decimal]) -> None:
    assert validate_multiple_of(value, multiple_of)


@pytest.mark.parametrize("value, multiple_of", [
    [2, 3],
    [2, 1.2],
    [9, 4],
    [Decimal("4"), Decimal("3")],
    [Decimal("3"), 2],
    [3.0, 2],
    [3.4, 2.2],
])
def test_fail_validate_multiple_of(value: Union[int, float, Decimal], multiple_of: Union[int, float, Decimal]) -> None:
    with pytest.raises(MultipleOfValidationError):
        validate_multiple_of(value, multiple_of)
