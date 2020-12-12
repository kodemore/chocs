from typing import Sized

from .errors import TypeValidationError
from .errors import UniqueValidationError
from .type_validators import validate_array
from .errors


def validate_unique(value: list) -> list:
    validate_array(value)

    unique_items = set()
    for item in value:
        if item in unique_items:
            raise UniqueValidationError()
        unique_items.add(item)

    return value


def validate_minimum_items(value: list, expected_minimum: int) -> list:
    validate_array(value)

    if len(value) >= expected_minimum:
        return value

    raise
