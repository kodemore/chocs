from typing import Callable, Dict, List, Union

from .errors import (
    AdditionalPropertyError,
    MaximumPropertyError,
    MinimumPropertyError,
    PropertyNameError,
    PropertyValueError,
    RequiredPropertyError,
    ValidationError,
)


def validate_object_properties(
    obj: dict, properties: Dict[str, Callable], additional_properties: Union[bool, Callable] = True,
) -> dict:

    property_length = 0
    for key, value in obj.items():
        property_length += 1
        if key not in properties:
            if not additional_properties:
                raise AdditionalPropertyError(property_name=key)
            if callable(additional_properties):
                try:
                    obj[key] = additional_properties(value)
                except PropertyValueError as error:
                    raise PropertyValueError(
                        property_name=key + "." + error.context["property_name"],
                        validation_error=error.context["validation_error"],
                    )
                except ValidationError as error:
                    raise PropertyValueError(
                        property_name=key, validation_error=str(error), sub_code=error.code,
                    )
                except ValueError as error:
                    raise PropertyValueError(property_name=key, validation_error=str(error))
            continue
        try:
            obj[key] = properties[key](value)
        except PropertyValueError as error:
            raise PropertyValueError(
                sub_code=error.code,
                property_name=key + "." + error.context["property_name"],
                validation_error=error.context["validation_error"],
            )
        except ValidationError as error:
            raise PropertyValueError(property_name=key, validation_error=str(error), sub_code=error.code)
        except ValueError as error:
            raise PropertyValueError(property_name=key, validation_error=str(error))

    return obj


def validate_object_property_names(obj: dict, property_names: Callable) -> dict:
    for name in obj.keys():
        try:
            property_names(name)
        except ValidationError as error:
            raise PropertyNameError(sub_code=error.code, property_name=name, validation_error=str(error))
        except ValueError as error:
            raise PropertyNameError(sub_code="error", property_name=name, validation_error=str(error))

    return obj


def validate_object_required_properties(obj: dict, required_properties: List[str]) -> dict:
    given_properties = obj.keys()
    missing_properties = [key for key in required_properties if key not in given_properties]

    if missing_properties:
        raise RequiredPropertyError(property_name=missing_properties[0])

    return obj


def validate_object_minimum_properties(obj: dict, expected_minimum: int) -> dict:
    if len(obj) < expected_minimum:
        raise MinimumPropertyError(expected_minimum=expected_minimum)
    return obj


def validate_object_maximum_properties(obj: dict, expected_maximum: int) -> dict:
    if len(obj) > expected_maximum:
        raise MaximumPropertyError(expected_maximum=expected_maximum)

    return obj


__all__ = [
    "validate_object_maximum_properties",
    "validate_object_minimum_properties",
    "validate_object_properties",
    "validate_object_property_names",
    "validate_object_required_properties",
]
