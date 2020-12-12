from typing import Any
from typing import Callable
from typing import Collection
from typing import Sized
from typing import Union

from .errors import TypeValidationError
from .errors import UniqueValidationError



def validate_items(
    value: Union[list, set, frozenset],
    item_validator: Callable
) -> Union[list, set, frozenset]:
    validated_items = []
    for item in value:
        validated_items.append(item_validator(item))

    if isinstance(value, set):
        return set(validated_items)

    if isinstance(value, frozenset):
        return frozenset(validated_items)

    return validated_items


def validate_unique(value: Collection[Any]) -> set:
    if not isinstance(value, Sized):
        raise TypeValidationError(expected_type="array")

    unique_items = set()
    for item in value:
        if item in unique_items:
            raise UniqueValidationError()
        unique_items.add(item)

    return unique_items

