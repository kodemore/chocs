from typing import Callable, List, Set, Union

from .errors import AdditionalItemsError, MaximumLengthError, MinimumLengthError, UniqueItemsValidationError
from .type_validators import validate_array


def validate_unique_items(value: list) -> list:
    validate_array(value)

    unique_items: Set = set()
    for item in value:
        for unique_item in unique_items:
            if item is unique_item:
                raise UniqueItemsValidationError()

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


def validate_tuple(value: list, item_validator: List[Callable], additional_items: Union[bool, Callable]) -> list:
    list_length = len(value)
    validators_length = len(item_validator)
    additional_items_validator = additional_items if callable(additional_items) else lambda x: x

    if list_length > validators_length and additional_items is False:
        raise AdditionalItemsError()

    for i in range(0, list_length):
        if i < validators_length:
            value[i] = item_validator[i](value[i])
            continue

        value[i] = additional_items_validator(value[i])  # type: ignore

    return value


__all__ = [
    "validate_items",
    "validate_maximum_items",
    "validate_minimum_items",
    "validate_unique_items",
    "validate_tuple",
]
