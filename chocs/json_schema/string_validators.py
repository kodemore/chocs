import re

from .errors import FormatValidationError
from .errors import MaximumLengthError
from .errors import MinimumLengthError
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
    raise MaximumLengthError(expected_minimum=expected_maximum)


def validate_match_pattern(value: str, pattern: str) -> str:
    if not re.search(pattern, value):
        raise FormatValidationError(expected_format=pattern)

    return value
