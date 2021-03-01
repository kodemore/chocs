from functools import partial
from typing import Any, Callable, Dict, List

from .array_validators import (
    validate_items,
    validate_maximum_items,
    validate_minimum_items,
    validate_tuple,
    validate_unique_items,
)
from .combining_validators import validate_all_of, validate_any_of, validate_not, validate_one_of
from .number_validators import (
    validate_exclusive_maximum,
    validate_exclusive_minimum,
    validate_maximum,
    validate_minimum,
    validate_multiple_of,
)
from .object_validators import (
    validate_object_dependencies,
    validate_object_maximum_properties,
    validate_object_minimum_properties,
    validate_object_properties,
    validate_object_property_names,
    validate_object_required_properties,
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
    if "anyOf" in schema:
        validators = [build_validator_from_schema(item) for item in schema["anyOf"]]
        return partial(validate_any_of, validators=validators)

    if "oneOf" in schema:
        validators = [build_validator_from_schema(item) for item in schema["oneOf"]]
        return partial(validate_one_of, validators=validators)

    if "allOf" in schema:
        validators = [build_validator_from_schema(item) for item in schema["allOf"]]
        return partial(validate_all_of, validators=validators)

    if "not" in schema:
        return partial(validate_not, validator=build_validator_from_schema(schema["not"]))

    if "type" in schema:
        return _build_validator_for_type(schema["type"], schema)

    if "enum" in schema:
        return _build_enum_validator(schema)

    raise ValueError("Could not build validator for passed schema")


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

    # default to string validation
    return _build_string_validator(definition)


def _build_string_validator(definition: Dict[str, Any]) -> Callable:
    validators = [validate_string]
    if "enum" in definition:
        validators.append(_build_enum_validator(definition))

    if "format" in definition:
        validators.append(partial(validate_string_format, format_name=definition["format"]))

    if "pattern" in definition:
        validators.append(partial(validate_string_pattern, pattern=definition["pattern"]))

    if "minLength" in definition:
        validators.append(partial(validate_minimum_length, expected_minimum=definition["minLength"]))

    if "maxLength" in definition:
        validators.append(partial(validate_maximum_length, expected_maximum=definition["maxLength"]))

    return partial(validate_all_of, validators=validators)


def _build_enum_validator(definition: Dict[str, Any]) -> Callable:
    return partial(validate_enum, values=definition["enum"])


def _build_boolean_validator() -> Callable:
    return validate_boolean


def _build_number_validator(base_validator: Callable, definition: Dict[str, Any]) -> Callable:
    validators = [base_validator]
    _add_range_validators(validators, definition)
    if "multipleOf" in definition:
        validators.append(partial(validate_multiple_of, multiple_of=definition["multipleOf"]))

    if "enum" in definition:
        validators.append(_build_enum_validator(definition))

    return partial(validate_all_of, validators=validators)


def _build_array_validator(definition: Dict[str, Any]) -> Callable:
    validators = [validate_array]
    if "minItems" in definition:
        validators.append(partial(validate_minimum_items, expected_minimum=definition["minItems"]))
    if "maxItems" in definition:
        validators.append(partial(validate_maximum_items, expected_maximum=definition["maxItems"]))

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


def _build_tuple_validator(definition: Dict[str, Any], validators: List[Callable]) -> None:
    items_validators = [build_validator_from_schema(item_schema) for item_schema in definition["items"]]
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
                    additional_items=build_validator_from_schema(definition["additionalItems"]),
                )
            )
    else:
        validators.append(partial(validate_tuple, item_validator=items_validators, additional_items=True))


def _build_object_validator(definition: Dict[str, Any]) -> Callable:
    validators = [validate_object]

    if "propertyNames" in definition:
        definition["propertyNames"]["type"] = "string"
        validators.append(
            partial(
                validate_object_property_names,
                property_names=build_validator_from_schema(definition["propertyNames"]),
            )
        )

    if "minProperties" in definition:
        validators.append(
            partial(
                validate_object_minimum_properties,
                expected_minimum=definition["minProperties"],
            )
        )

    if "maxProperties" in definition:
        validators.append(
            partial(
                validate_object_maximum_properties,
                expected_maximum=definition["maxProperties"],
            )
        )

    if "required" in definition and definition["required"]:
        validators.append(
            partial(
                validate_object_required_properties,
                required_properties=definition["required"],
            )
        )

    if "dependencies" in definition:
        validators.append(partial(validate_object_dependencies, dependencies=definition["dependencies"]))

    property_validator_settings: Dict[str, Any] = {}

    if "properties" in definition:
        properties_validators = {
            property_name: build_validator_from_schema(property_schema)
            for property_name, property_schema in definition["properties"].items()
        }

        property_validator_settings["properties"] = properties_validators

    if "additionalProperties" in definition:
        if isinstance(definition["additionalProperties"], bool):
            property_validator_settings["additional_properties"] = definition["additionalProperties"]
        else:
            property_validator_settings["additional_properties"] = build_validator_from_schema(
                definition["additionalProperties"]
            )

    if "patternProperties" in definition:
        property_validator_settings["pattern_properties"] = {
            key: build_validator_from_schema(value) for key, value in definition["patternProperties"].items()
        }

    if property_validator_settings:
        validators.append(partial(validate_object_properties, **property_validator_settings))

    return partial(validate_all_of, validators=validators)


def _add_range_validators(validators: List[Callable], definition: Dict[str, Any]) -> None:
    if "minimum" in definition:
        validators.append(partial(validate_minimum, expected_minimum=definition["minimum"]))
    if "inclusiveMinimum" in definition:
        validators.append(partial(validate_minimum, expected_minimum=definition["inclusiveMinimum"]))

    if "maximum" in definition:
        validators.append(partial(validate_maximum, expected_maximum=definition["maximum"]))
    if "inclusiveMaximum" in definition:
        validators.append(partial(validate_maximum, expected_maximum=definition["inclusiveMaximum"]))

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
