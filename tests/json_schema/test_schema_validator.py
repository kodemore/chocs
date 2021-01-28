import pytest

from chocs.json_schema import build_validator_from_schema
from chocs.json_schema.errors import (
    AdditionalItemsError,
    AdditionalPropertyError,
    EnumValidationError,
    FormatValidationError,
    LengthValidationError,
    MultipleOfValidationError,
    PropertyError,
    PropertyValueError,
    RangeValidationError,
    RequiredPropertyError,
    TypeValidationError,
    UniqueItemsValidationError,
)


def test_can_build_validator_for_boolean_type() -> None:
    validate = build_validator_from_schema({"type": "boolean"})

    assert validate(True)
    assert not validate(False)

    with pytest.raises(TypeValidationError) as e:
        validate(1)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'bool'> type. "
        "Actual type passed was <class 'int'>"
    )


def test_can_build_validator_for_number_type() -> None:
    # validate integer
    validate = build_validator_from_schema({"type": "integer"})
    assert validate(1)
    with pytest.raises(TypeValidationError) as e:
        validate(5.0)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'int'> type. "
        "Actual type passed was <class 'float'>"
    )

    # validate number
    validate = build_validator_from_schema({"type": "number"})
    assert validate(1.0)
    with pytest.raises(TypeValidationError) as e:
        validate("4")
    assert e.value.args[0] == (
        "Passed value must be valid <class 'numbers.Number'> type. "
        "Actual type passed was <class 'str'>"
    )

    # validate minimum
    validate = build_validator_from_schema({"type": "integer", "minimum": 5})
    assert validate(5)
    with pytest.raises(RangeValidationError):
        validate(4)

    # validate maximum
    validate = build_validator_from_schema({"type": "integer", "maximum": 5})
    assert validate(5)
    with pytest.raises(RangeValidationError):
        validate(6)

    # validate multiple of
    validate = build_validator_from_schema({"type": "integer", "multipleOf": 5})
    assert validate(5)
    with pytest.raises(MultipleOfValidationError):
        validate(6)

    # validate maximum and minimum together
    validate = build_validator_from_schema(
        {"type": "integer", "minimum": 2, "maximum": 5}
    )
    assert validate(2)
    assert validate(3)
    assert validate(4)
    assert validate(5)
    with pytest.raises(RangeValidationError):
        validate(1)
    with pytest.raises(RangeValidationError):
        validate(6)

    # validate enum
    validate = build_validator_from_schema({"type": "integer", "enum": [1, 3, 6]})
    assert validate(1)
    assert validate(3)
    assert validate(6)
    with pytest.raises(EnumValidationError):
        validate(2)
    with pytest.raises(TypeValidationError):
        validate("a")
    assert e.value.args[0] == (
        "Passed value must be valid <class 'numbers.Number'> type. "
        "Actual type passed was <class 'str'>"
    )


def test_can_build_validator_for_string_type() -> None:

    # validate type
    validate = build_validator_from_schema({"type": "string"})
    assert validate("a")
    with pytest.raises(TypeValidationError) as e:
        validate(5.0)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'str'> type. "
        "Actual type passed was <class 'float'>"
    )

    # validate format
    validate = build_validator_from_schema({"type": "string", "format": "email"})
    assert validate("test@email.com")
    with pytest.raises(FormatValidationError):
        validate("a")

    # validate pattern
    validate = build_validator_from_schema({"type": "string", "pattern": "[0-9][a-e]"})
    assert validate("1a")
    assert validate("0a")
    assert validate("9e")
    with pytest.raises(FormatValidationError):
        validate("a")
    with pytest.raises(FormatValidationError):
        validate("0")

    # validate min length
    validate = build_validator_from_schema({"type": "string", "minLength": 3})
    assert validate("aaa")
    assert validate("abab")
    with pytest.raises(LengthValidationError):
        validate("a")

    # validate max length
    validate = build_validator_from_schema({"type": "string", "maxLength": 3})
    assert validate("aa")
    assert validate("aaa")
    with pytest.raises(LengthValidationError):
        validate("aaaa")

    # validate enum
    validate = build_validator_from_schema(
        {"type": "string", "enum": ["a", "bb", "ab"]}
    )
    assert validate("a")
    assert validate("bb")
    assert validate("ab")
    with pytest.raises(EnumValidationError):
        validate("aaaa")


def test_can_build_validator_for_array() -> None:
    # validate type
    validate = build_validator_from_schema({"type": "array"})
    assert validate([1, 2, 3])
    with pytest.raises(TypeValidationError) as e:
        validate("a")
    assert e.value.args[0] == (
        "Passed value must be valid array type. "
        "Actual type passed was <class 'str'>"
    )

    # validate min items
    validate = build_validator_from_schema({"type": "array", "minItems": 2})
    assert validate([1, 2])
    with pytest.raises(LengthValidationError):
        validate([1])

    # validate max items
    validate = build_validator_from_schema({"type": "array", "maxItems": 2})
    assert validate([1, 2])
    with pytest.raises(LengthValidationError):
        validate([1, 2, 3])

    # validate unique
    validate = build_validator_from_schema(
        {"type": "array", "minItems": 2, "uniqueItems": True}
    )
    assert validate([1, 2])
    assert validate([1, 2, 3])
    with pytest.raises(LengthValidationError):
        validate([1])
    with pytest.raises(UniqueItemsValidationError):
        validate([1, 1])

    # validate items
    validate = build_validator_from_schema(
        {"type": "array", "items": {"type": "integer"}}
    )
    assert validate([1, 2, 3])
    with pytest.raises(TypeValidationError):
        assert validate([1, 2, "a"])
    assert e.value.args[0] == (
        "Passed value must be valid array type. "
        "Actual type passed was <class 'str'>"
    )
    validate = build_validator_from_schema(
        {"type": "array", "items": {"type": "string", "format": "email"}}
    )
    assert validate(["tom@mail.com", "bob@mail.com"])
    with pytest.raises(FormatValidationError):
        assert validate(["a"])

    # validate tuple
    validate = build_validator_from_schema(
        {
            "type": "array",
            "items": [
                {"type": "string", "format": "email"},
                {"type": "string", "minLength": 2},
                {"type": "integer", "minimum": 0, "maximum": 150,},
            ],
        }
    )
    assert validate(["bob@email.com", "Bob", 12])
    assert validate(["jen@email.com", "Jenny", 99, "aaa"])
    with pytest.raises(FormatValidationError):
        assert validate(["bob", "bob", 10])

    validate = build_validator_from_schema(
        {
            "type": "array",
            "additionalItems": False,
            "items": [
                {"type": "string", "format": "email"},
                {"type": "string", "minLength": 2},
                {"type": "integer", "minimum": 0, "maximum": 150,},
            ],
        }
    )
    assert validate(["bob@email.com", "Bob", 12])
    with pytest.raises(AdditionalItemsError):
        assert validate(["jen@email.com", "Jenny", 99, "aaa"])

    validate = build_validator_from_schema(
        {
            "type": "array",
            "additionalItems": {"type": "string"},
            "items": [
                {"type": "string", "format": "email"},
                {"type": "string", "minLength": 2},
                {"type": "integer", "minimum": 0, "maximum": 150},
            ],
        }
    )
    assert validate(["bob@email.com", "Bob", 12])
    assert validate(["bob@email.com", "Bob", 12, "a"])
    assert validate(["bob@email.com", "Bob", 12, "a", "b"])
    with pytest.raises(TypeValidationError) as e:
        assert validate(["bob@email.com", "Bob", 12, 10])
    assert e.value.args[0] == (
        "Passed value must be valid <class 'str'> type. "
        "Actual type passed was <class 'int'>"
    )
    with pytest.raises(RangeValidationError):
        assert validate(["bob@email.com", "Bob", 151])


def test_can_build_validator_for_object() -> None:

    # validate type
    validate = build_validator_from_schema({"type": "object"})
    assert validate({"a": 1})
    with pytest.raises(TypeValidationError) as e:
        validate("a")
    assert e.value.args[0] == (
        "Passed value must be valid object type. "
        "Actual type passed was <class 'str'>"
    )

    # validate properties
    validate = build_validator_from_schema(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string"},
                "address": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "street_no": {"type": "number"},
                        "street_name": {"type": "string"},
                    },
                },
            },
        }
    )
    assert validate(
        {
            "email": "bob@email.com",
            "name": "Bob Bobber",
            "address": {
                "city": "Bob Land",
                "street_no": 10,
                "street_name": "Bob Street",
            },
        }
    )
    assert validate({"email": "bob@email.com", "name": "Bob Bobber"})
    with pytest.raises(PropertyValueError):
        assert validate({"email": "email", "name": "Bob"})
    with pytest.raises(PropertyValueError) as error:
        assert validate(
            {"email": "bob@email.com", "name": "Bob", "address": {"city": 123}}
        )

    # turn off additional properties
    validate = build_validator_from_schema(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string"},
            },
            "additionalProperties": False,
        }
    )
    assert validate({"email": "bob@email.com", "name": "Bob Bobber"})
    with pytest.raises(AdditionalPropertyError):
        validate({"email": "bob@email.com", "name": "Bob Bobber", "address": "aa"})

    # validate additional properties
    validate = build_validator_from_schema(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string"},
            },
            "additionalProperties": {"type": "string"},
        }
    )
    assert validate({"email": "bob@email.com", "name": "Bob Bobber"})
    assert validate(
        {"email": "bob@email.com", "name": "Bob Bobber", "address": "Bob Land"}
    )
    with pytest.raises(PropertyValueError):
        validate({"email": "bob@email.com", "name": "Bob Bobber", "address": 123})

    # validate required properties
    validate = build_validator_from_schema(
        {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "name": {"type": "string"},
            },
            "required": ["email", "name"],
        }
    )
    assert validate({"email": "bob@email.com", "name": "Bob Bobber"})
    with pytest.raises(RequiredPropertyError):
        validate({"email": "bob@email.com"})

    # validate property names
    validate = build_validator_from_schema(
        {
            "type": "object",
            "propertyNames": {"type": "string", "pattern": "[a-z]+_[0-9]"},
        }
    )
    assert validate({"test_1": "a", "test_2": "b"})
    with pytest.raises(PropertyError):
        validate({"email": "bob@email.com"})

    # validate minimum properties
    validate = build_validator_from_schema({"type": "object", "minProperties": 2,})
    validate({"a": 1, "b": 2})
    with pytest.raises(PropertyError):
        validate({"a": 1})

    # validate maximum properties
    validate = build_validator_from_schema({"type": "object", "maxProperties": 2,})
    validate({"a": 1, "b": 2})
    with pytest.raises(PropertyError):
        validate({"a": 1, "b": 2, "c": 3})

