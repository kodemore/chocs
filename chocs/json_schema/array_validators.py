from typing import Callable

from .errors import MaximumLengthError
from .errors import MinimumLengthError
from .errors import UniqueValidationError
from .type_validators import validate_array


def validate_unique(value: list) -> list:
    validate_array(value)

    unique_items = set()
    for item in value:
        for unique_item in unique_items:
            if item is unique_item:
                raise UniqueValidationError()
            
        unique_items.add(item)

    return value


def validate_minimum_items(value: list, expected_minimum: int) -> list:
    validate_array(value)

    if len(value) >= expected_minimum:
        return value

    raise MinimumLengthError(expected_minimum=expected_minimum)


def validate_maximum_items(value: list, expected_maximum: int) -> list:
    validate_array(value)

    if len(value) <= expected_maximum:
        return value

    raise MaximumLengthError(expected_maximum=expected_maximum)


def validate_items(value: list, item_validator: Callable) -> list:
    validate_array(value)

    return [item_validator(item) for item in value]
