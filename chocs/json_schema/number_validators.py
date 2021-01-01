from decimal import Decimal
from typing import Union

from .errors import (
    MaximumExclusiveRangeError,
    MaximumRangeError,
    MinimumExclusiveRangeError,
    MinimumRangeError,
    MultipleOfValidationError,
)

Number = Union[int, float, Decimal]


def validate_multiple_of(value: Number, multiple_of: Number) -> Number:
    if not value % multiple_of == 0:  # type: ignore
        raise MultipleOfValidationError(multiple_of=multiple_of)

    return value


def validate_minimum(value: Number, expected_minimum: Number) -> Number:
    if value >= expected_minimum:
        return value

    raise MinimumRangeError(expected_minimum=expected_minimum)


def validate_exclusive_minimum(value: Number, expected_minimum: Number) -> Number:
    if value > expected_minimum:
        return value

    raise MinimumExclusiveRangeError(expected_minimum=expected_minimum)


def validate_maximum(value: Number, expected_maximum: Number) -> Number:
    if value <= expected_maximum:
        return value

    raise MaximumRangeError(expected_maximum=expected_maximum)


def validate_exclusive_maximum(value: Number, expected_maximum: Number) -> Number:
    if value < expected_maximum:
        return value

    raise MaximumExclusiveRangeError(expected_maximum=expected_maximum)


__all__ = [
    "validate_exclusive_maximum",
    "validate_exclusive_minimum",
    "validate_maximum",
    "validate_minimum",
    "validate_multiple_of",
]
