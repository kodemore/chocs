from typing import Any


class ValidationError(ValueError):
    code: str
    message: str

    def __init__(self, *args, **kwargs: Any):
        if "code" in kwargs:
            self.code = kwargs["code"]

        self.context = kwargs
        if args:
            super().__init__(*args)
        else:
            super().__init__(str(self))

    def __bool__(self) -> bool:
        return False

    def __str__(self) -> str:
        return self.message.format(**self.context)


class TypeValidationError(ValidationError):
    code = "type_error"
    message = "Passed value must be valid {expected_type} type."


class EnumValidationError(ValidationError):
    code = "enum_error"
    message = "Passed value must be one of: {expected_values} type."


class FormatValidationError(ValidationError):
    code = "format_error"
    message = "Passed value must be valid string format: {expected_format}."


class UniqueValidationError(TypeValidationError):
    code = "unique_error"
    message = "Passed value must contain only unique items."


class ArithmeticValidationError(ValidationError, ArithmeticError):
    code = "arithmetic_error"
    message = "Passed value is invalid."


class MultipleOfValidationError(ArithmeticValidationError):
    code = "multiple_of_error"
    message = "Passed value must be multiple of `{multiple_of}`"


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


class RequiredFieldError(ValidationError):
    code = "required_field"
    message = "Field `{required_field}` is required."
