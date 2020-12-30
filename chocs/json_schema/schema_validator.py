from functools import partial
from typing import Any, Callable, Dict, List

from .array_validators import (
    validate_items,
    validate_maximum_items,
    validate_minimum_items,
    validate_tuple,
    validate_unique_items,
)
from .combining_validators import validate_all_of
from .number_validators import (
    validate_exclusive_maximum,
    validate_exclusive_minimum,
    validate_maximum,
    validate_minimum,
    validate_multiple_of,
)
from .string_validators import (
    validate_maximum_length,
    validate_minimum_length,
    validate_string_format,
    validate_string_pattern,
)
from .type_validators import (
    validate_array,
    validate_boolean,
    validate_enum,
    validate_integer,
    validate_number,
    validate_object,
    validate_string,
)


def build_validator_from_schema(schema: Dict[str, Any]) -> Callable:
    return _build_validator_for_type(schema["type"], schema)


def _build_validator_for_type(schema_type: str, definition: Dict[str, Any]) -> Callable:
    if schema_type == "boolean":
        return _build_boolean_validator()

    if schema_type == "integer":
        return _build_number_validator(validate_integer, definition)

    if schema_type == "number":
        return _build_number_validator(validate_number, definition)

    if schema_type == "string":
        return _build_string_validator(definition)

    if schema_type == "array":
        return _build_array_validator(definition)

    if schema_type == "object":
        return _build_object_validator(definition)


def _build_string_validator(definition: Dict[str, Any]) -> Callable:
    validators = [validate_string]
    if "enum" in definition:
        validators.append(_build_enum_validator(definition))

    if "format" in definition:
        validators.append(
            partial(validate_string_format, format_name=definition["format"])
        )

    if "pattern" in definition:
        validators.append(
            partial(validate_string_pattern, pattern=definition["pattern"])
        )

    if "minLength" in definition:
        validators.append(
            partial(validate_minimum_length, expected_minimum=definition["minLength"])
        )

    if "maxLength" in definition:
        validators.append(
            partial(validate_maximum_length, expected_maximum=definition["maxLength"])
        )

    return partial(validate_all_of, validators=validators)


def _build_enum_validator(definition: Dict[str, Any]) -> Callable:
    return partial(validate_enum, values=definition["enum"])


def _build_boolean_validator() -> Callable:
    return validate_boolean


def _build_number_validator(
    base_validator: Callable, definition: Dict[str, Any]
) -> Callable:
    validators = [base_validator]
    _add_range_validators(validators, definition)
    if "multipleOf" in definition:
        validators.append(
            partial(validate_multiple_of, multiple_of=definition["multipleOf"])
        )

    if "enum" in definition:
        validators.append(_build_enum_validator(definition))

    return partial(validate_all_of, validators=validators)


def _build_array_validator(definition: Dict[str, Any]) -> Callable:
    validators = [validate_array]
    if "minItems" in definition:
        validators.append(
            partial(validate_minimum_items, expected_minimum=definition["minItems"])
        )
    if "maxItems" in definition:
        validators.append(
            partial(validate_maximum_items, expected_maximum=definition["maxItems"])
        )

    if "uniqueItems" in definition and definition["uniqueItems"]:
        validators.append(validate_unique_items)

    if "items" in definition:
        if isinstance(definition["items"], list):
            _build_tuple_validator(definition, validators)
        elif isinstance(definition["items"], dict):
            validators.append(
                partial(
                    validate_items,
                    item_validator=build_validator_from_schema(definition["items"]),
                )
            )

    return partial(validate_all_of, validators=validators)


def _build_tuple_validator(
    definition: Dict[str, Any], validators: List[Callable]
) -> None:
    items_validators = [
        build_validator_from_schema(item_schema) for item_schema in definition["items"]
    ]
    if "additionalItems" in definition:
        if isinstance(definition["additionalItems"], bool):
            validators.append(
                partial(
                    validate_tuple,
                    item_validator=items_validators,
                    additional_items=definition["additionalItems"],
                )
            )
        else:
            validators.append(
                partial(
                    validate_tuple,
                    item_validator=items_validators,
                    additional_items=build_validator_from_schema(
                        definition["additionalItems"]
                    ),
                )
            )
    else:
        validators.append(
            partial(
                validate_tuple, item_validator=items_validators, additional_items=True
            )
        )


def _build_object_validator(definition: Dict[str, Any]) -> Callable:
    return validate_object


def _add_range_validators(
    validators: List[Callable], definition: Dict[str, Any]
) -> None:
    if "minimum" in definition:
        validators.append(
            partial(validate_minimum, expected_minimum=definition["minimum"])
        )
    if "inclusiveMinimum" in definition:
        validators.append(
            partial(validate_minimum, expected_minimum=definition["inclusiveMinimum"])
        )

    if "maximum" in definition:
        validators.append(
            partial(validate_maximum, expected_maximum=definition["maximum"])
        )
    if "inclusiveMaximum" in definition:
        validators.append(
            partial(validate_maximum, expected_maximum=definition["inclusiveMaximum"])
        )

    if "exclusiveMinimum" in definition:
        validators.append(
            partial(
                validate_exclusive_minimum,
                expected_minimum=definition["exclusiveMinimum"],
            )
        )
    if "exclusiveMaximum" in definition:
        validators.append(
            partial(
                validate_exclusive_maximum,
                expected_maximum=definition["exclusiveMaximum"],
            )
        )