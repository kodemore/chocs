from typing import Any, Callable, Iterable

from .errors import ValidationError


def validate_all(value: Any, validators: Iterable[Callable]) -> Any:
    for validate in validators:
        value = validate(value)
    return value


def validate_any(value: Any, validators: Iterable[Callable]) -> Any:
    for validate in validators:
        try:
            validate(value)
            return value
        except ValueError:
            continue

    raise ValidationError("Value could not be validated", code="any_error")


def validate_one_of(value: Any, validators: Iterable[Callable]) -> Any:
    valid_count = 0
    for validate in validators:
        try:
            validate(value)
            valid_count += 1
        except ValueError:
            continue

        if valid_count > 1:
            raise ValidationError(
                "Value should only match one of validators", code="one_of_error"
            )

    return value


def validate_not(value: Any, validator: Callable) -> Any:
    try:
        validator(value)
        raise ValidationError(
            "Value should not match passed validator", code="not_error"
        )
    except ValueError:
        return value
