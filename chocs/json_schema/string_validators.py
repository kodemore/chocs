import re
from typing import Any

from .errors import FormatValidationError, MaximumLengthError, MinimumLengthError
from .string_format import StringFormat
from .type_validators import validate_string


def validate_minimum_length(value: str, expected_minimum: int) -> str:
    validate_string(value)
    if len(value) >= expected_minimum:
        return value

    raise MinimumLengthError(expected_minimum=expected_minimum)


def validate_maximum_length(value: str, expected_maximum: int) -> str:
    validate_string(value)
    if len(value) <= expected_maximum:
        return value
    raise MaximumLengthError(expected_maximum=expected_maximum)


def validate_string_pattern(value: str, pattern: str) -> str:
    if not re.search(pattern, value):
        raise FormatValidationError(expected_format=pattern)

    return value


def validate_string_format(value: str, format_name: str) -> Any:
    format_validator = StringFormat[format_name]

    return format_validator(value)


__all__ = [
    "validate_maximum_length",
    "validate_minimum_length",
    "validate_string_format",
    "validate_string_pattern",
]
