import re
from typing import Any, Callable, Dict, List, Optional, Union

from .errors import (
    AdditionalPropertyError,
    MaximumPropertyError,
    MinimumPropertyError,
    PropertyNameError,
    PropertyValueError,
    RequiredPropertyError,
    ValidationError,
    MissingDependencyError,
)


def validate_object_properties(
    obj: dict,
    properties: Dict[str, Callable] = None,
    additional_properties: Union[bool, Callable] = True,
    pattern_properties: Dict[str, Callable] = None,
) -> dict:
    properties = properties if properties is not None else {}
    for key, value in obj.items():
        if key in properties:
            try:
                obj[key] = properties[key](value)
                continue
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

        if not additional_properties and not pattern_properties:
            raise AdditionalPropertyError(property_name=key)

        if pattern_properties:
            property_validator: Optional[Callable] = None
            for property_pattern, tmp_validator in pattern_properties.items():
                if re.search(property_pattern, key):
                    property_validator = tmp_validator
                    break

            if property_validator:
                obj[key] = property_validator(value)
                continue

            if additional_properties is False:
                raise AdditionalPropertyError(property_name=key)

        if additional_properties is False:
            raise AdditionalPropertyError(property_name=key)

        if additional_properties is True:
            continue

        try:
            obj[key] = additional_properties(value)  # type: ignore
        except PropertyValueError as error:
            raise PropertyValueError(
                property_name=key + "." + error.context["property_name"],
                validation_error=error.context["validation_error"],
            )
        except ValidationError as error:
            raise PropertyValueError(
                property_name=key,
                validation_error=str(error),
                sub_code=error.code,
            )
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


def validate_object_dependencies(obj: dict, dependencies: Dict[str, List[str]]) -> dict:
    for field_name, field_dependencies in dependencies.items():
        if field_name not in obj:
            continue
        if not all(k in obj for k in field_dependencies):
            raise MissingDependencyError(property=field_name, dependencies=field_dependencies)

    return obj


__all__ = [
    "validate_object_dependencies",
    "validate_object_maximum_properties",
    "validate_object_minimum_properties",
    "validate_object_properties",
    "validate_object_property_names",
    "validate_object_required_properties",
]
