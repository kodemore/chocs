from numbers import Number
from typing import Any
from typing import Collection
from typing import List
from typing import Union
from typing import Callable

from .errors import EnumValidationError
from .errors import TypeValidationError


def validate_string(value: Any) -> str:
    if isinstance(value, str):
        return value

    raise TypeValidationError(value=value, expected_type=str)


def validate_boolean(value: Any) -> bool:
    if value is True or value is False:
        return value

    raise TypeValidationError(expected_type=bool)


def validate_enum(value: Any, values: List[Union[str, int, float]]) -> Union[str, int, float]:
    if value in values:
        return value

    raise EnumValidationError(expected_values=values)


def validate_integer(value: Any) -> int:
    if isinstance(value, int) and value is not True and value is not False:
        return value

    raise TypeValidationError(expected_type=int)


def validate_number(value: Any) -> Number:
    if isinstance(value, Number):
        return value

    raise TypeValidationError(expected_type=Number)


def validate_array(value: list) -> list:
    if not isinstance(value, list):
        raise TypeValidationError(expected_type="array")

    return value


def validate_nullable(value: Any, validator: Callable) -> Any:
    if value is None:
        return None

    return validator(value)
