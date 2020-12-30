from typing import Callable, Dict, List, Union

from .errors import (
    AdditionalPropertyError,
    MaximumPropertyError,
    MinimumPropertyError,
    PropertyValueError,
    RequiredPropertyError,
)


def validate_object_properties(
    obj: dict,
    properties: Dict[str, Callable],
    extra_properties: Union[bool, Callable] = True,
    required_properties: List[str] = [],
    minimum_properties: int = 0,
    maximum_properties: int = 0,
) -> dict:

    property_length = 0
    for key, value in obj.items():
        property_length += 1
        if key not in properties:
            if not extra_properties:
                raise AdditionalPropertyError(property_name=key)
            if callable(extra_properties):
                obj[key] = extra_properties(value)
            continue
        try:
            obj[key] = properties[key](value)
        except PropertyValueError as error:
            raise PropertyValueError(
                property_name=key + "." + error.context["property_name"],
                validation_error=error.context["validation_error"],
            )
        except ValueError as error:
            raise PropertyValueError(property_name=key, validation_error=str(error))

    given_properties = obj.keys()
    missing_properties = [
        key for key in required_properties if key not in given_properties
    ]

    if missing_properties:
        raise RequiredPropertyError(property_name=missing_properties[0])

    if minimum_properties and property_length < minimum_properties:
        raise MinimumPropertyError(expected_minimum=minimum_properties)

    if maximum_properties and property_length > maximum_properties:
        raise MaximumPropertyError(expected_maximum=maximum_properties)

    return obj


__all__ = [
    "validate_object_properties",
]
