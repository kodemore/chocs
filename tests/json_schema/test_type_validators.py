import pytest
from typing import Any, Callable

from chocs.json_schema.errors import EnumValidationError, TypeValidationError
from chocs.json_schema.validators import (
    validate_array,
    validate_boolean,
    validate_enum,
    validate_integer,
    validate_nullable,
    validate_number,
    validate_string,
)


@pytest.mark.parametrize("value", [[], [1, 2, 3],])
def test_pass_validate_array(value: Any) -> None:
    assert validate_array(value) == value


@pytest.mark.parametrize("value", [1, "", ()])
def test_fail_validate_array(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_array(value)
    assert e.value.args[0] == (
        "Passed value must be valid array type. "
        f"Actual type passed was {type(value)}"
    )


@pytest.mark.parametrize("value", [True, False,])
def test_pass_validate_boolean(value: Any) -> None:
    assert validate_boolean(value) == value


@pytest.mark.parametrize("value", [1, "True", "False", 0,])
def test_fail_validate_boolean(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_boolean(value)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'bool'> type. "
        f"Actual type passed was {type(value)}"
    )


@pytest.mark.parametrize(
    "value, expected_values",
    [[1, [1, 2, 3]], ["ok", [1, 2, "ok"]], ["no", (1, 2, "no")]],
)
def test_pass_validate_enum(value: Any, expected_values: list) -> None:
    assert validate_enum(value, expected_values) == value


@pytest.mark.parametrize("value, expected_values", [[1, [0]], [False, ["False", 0, 2]]])
def test_fail_validate_enum(value: Any, expected_values: list) -> None:
    with pytest.raises(EnumValidationError):
        validate_enum(value, expected_values)


@pytest.mark.parametrize("value", [1, 123, 12453,])
def test_pass_validate_integer(value: Any) -> None:
    assert validate_integer(value) == value


@pytest.mark.parametrize("value", [True, False, "True", "False", 1.2,])
def test_fail_validate_integer(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_integer(value)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'int'> type. "
        f"Actual type passed was {type(value)}"
    )


@pytest.mark.parametrize(
    "value, validator",
    [
        [None, validate_integer],
        [1, validate_integer],
        [None, validate_string],
        ["a", validate_string],
    ],
)
def test_pass_validate_nullable(value: Any, validator: Callable) -> None:
    assert validate_nullable(value, validator) == value


@pytest.mark.parametrize(
    "value, validator",
    [["a", validate_integer], [False, validate_integer], [1, validate_string],],
)
def test_fail_validate_nullable(value: Any, validator: Callable) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_nullable(value, validator)


@pytest.mark.parametrize("value", [1, 123.124, 12453.2, 0,])
def test_pass_validate_number(value: Any) -> None:
    assert validate_number(value) == value


@pytest.mark.parametrize("value", [True, False, "True", "False", [0]])
def test_fail_validate_number(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_number(value)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'numbers.Number'> type. "
        f"Actual type passed was {type(value)}"
    )


@pytest.mark.parametrize("value", ["cat", "dog", "", "   "])
def test_pass_validate_string(value: Any) -> None:
    assert validate_string(value) == value


@pytest.mark.parametrize("value", [True, False, [0], 2])
def test_fail_validate_string(value: Any) -> None:
    with pytest.raises(TypeValidationError) as e:
        validate_string(value)
    assert e.value.args[0] == (
        "Passed value must be valid <class 'str'> type. "
        f"Actual type passed was {type(value)}"
    )
