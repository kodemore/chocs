from typing import Any


class ValidationError(ValueError):
    code: str
    message: str

    def __init__(self, *args, **kwargs: Any):
        if "code" in kwargs:
            self.code = kwargs["code"]

        self.context = kwargs
        self.code = self.code.format(**self.context)
        if args:
            super().__init__(*args)
        else:
            super().__init__(str(self))

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return self.message.format(**self.context)


class InvalidInputValidationError(ValidationError):
    code = "input_error"
    message = "Request body is invalid or malformed: {message}."


class TypeValidationError(ValidationError):
    code = "type_error"
    message = "Passed value must be valid {expected_type} type. " "Actual type passed was {actual_type}."


class EnumValidationError(ValidationError):
    code = "enum_error"
    message = "Passed value must be one of: {expected_values} type."


class FormatValidationError(ValidationError):
    code = "format_error"
    message = "Passed value must be valid string format: {expected_format}."


class UniqueItemsValidationError(TypeValidationError):
    code = "unique_items_error"
    message = "Passed value must contain only unique items."


class AdditionalItemsError(ValidationError):
    code = "additional_items_error"
    message = "Additional items in the array are not accepted."


class ArithmeticValidationError(ValidationError, ArithmeticError):
    code = "arithmetic_error"
    message = "Passed value is invalid."


class MultipleOfValidationError(ArithmeticValidationError):
    code = "multiple_of_error"
    message = "Passed value must be multiple of `{multiple_of}`."


class LengthValidationError(ArithmeticValidationError):
    pass


class RangeValidationError(ArithmeticValidationError):
    pass


class MinimumRangeError(RangeValidationError):
    code = "minimum_error"
    message = "Passed value must be greater or equal to set minimum `{expected_minimum}`."


class MinimumExclusiveRangeError(MinimumRangeError):
    code = "minimum_error"
    message = "Passed value must be greater than set minimum `{expected_minimum}`."


class MaximumRangeError(RangeValidationError):
    code = "maximum_error"
    message = "Passed value must be lower or equal to set maximum `{expected_maximum}`."


class MaximumExclusiveRangeError(MaximumRangeError):
    code = "maximum_exclusive_error"
    message = "Passed value must be lower than set maximum `{expected_maximum}`."


class MinimumLengthError(LengthValidationError):
    code = "minimum_error"
    message = "Passed value's length must be greater or equal to set minimum `{expected_minimum}`."


class MaximumLengthError(LengthValidationError):
    code = "maximum_error"
    message = "Passed value's length must be lower or equal to set maximum `{expected_maximum}`."


class PropertyError(ValidationError):
    code = "property_error"
    message = "Problem with property {property_name}."
    property_name = "unknown"

    def __init__(self, *args, **kwargs: Any):
        if "property_name" in kwargs:
            self.property_name = kwargs["property_name"]

        super().__init__(*args, **kwargs)


class RequiredPropertyError(PropertyError):
    code = "required_property_error"
    message = "Property `{property_name}` is required."


class PropertyValueError(PropertyError):
    code = "property_value_error:{sub_code}"
    message = "Property `{property_name}` failed to pass validation: {validation_error}"


class PropertyNameError(PropertyError):
    code = "property_name_error:{sub_code}"
    message = "Property name `{property_name}` is invalid: {validation_error}."


class AdditionalPropertyError(PropertyError):
    code = "additional_property_error"
    message = "Object does not expect additional properties. Property `{property_name}` is not allowed."


class MinimumPropertyError(PropertyError):
    code = "minimum_property_error"
    message = "The number of properties is lower than expected minimum: {expected_minimum}."


class MaximumPropertyError(PropertyError):
    code = "maximum_property_error"
    message = "The number of properties is greater than expected maximum: {expected_maximum}."


class MissingDependencyError(PropertyError):
    code = "missing_property_error"
    message = "Property `{property}` requires {dependencies} to be provided."
