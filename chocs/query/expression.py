from abc import ABC
from typing import Union, List

ExpressionValue = Union[str, int, float, None]


def _cast_value(value: str) -> ExpressionValue:
    if not value:
        return None

    if value.isnumeric():
        return int(value)

    if value.replace(".", "", 1).isdigit():
        return float(value)

    return value


class Expression(ABC):
    ...


class EqualExpression(Expression):
    value: ExpressionValue

    def __init__(self, value: ExpressionValue):
        self.value = value

    def __str__(self) -> str:
        return f"{self.value}"


class GreaterThanExpression(Expression):
    value: ExpressionValue

    def __init__(self, value: ExpressionValue):
        self.value = value

    def __str__(self) -> str:
        return f">{self.value}"


class LowerThanExpression(Expression):
    value: ExpressionValue

    def __init__(self, value: ExpressionValue):
        self.value = value

    def __str__(self) -> str:
        return f"<{self.value}"


class RangeExpression(Expression):
    start: ExpressionValue
    end: ExpressionValue

    def __init__(self, start: ExpressionValue, end: ExpressionValue):
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.start}..{self.end}"


class PatternExpression(Expression):
    start: ExpressionValue
    end: ExpressionValue

    def __init__(self, start: str, end: str):
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.start}*{self.end}"


class InExpression(Expression):
    values: List[ExpressionValue]

    def __init__(self, values: List[ExpressionValue]):
        self.values = values

    def __str__(self) -> str:
        return ",".join([str(value) for value in self.values])


def parse_expression(value: Union[list, str, int, float, bool]) -> Expression:
    if isinstance(value, list):
        return InExpression(value)

    if not isinstance(value, str):
        return EqualExpression(value)

    # edge cases
    if value in ("..", ">", "<", "*", ",", '"'):
        return EqualExpression(value)

    # escaping
    if value.startswith('"'):
        return EqualExpression(value[1:-1])

    if value.startswith(">"):
        return GreaterThanExpression(_cast_value(value[1:]))

    if value.startswith("<"):
        return LowerThanExpression(_cast_value(value[1:]))

    if ".." in value:
        range_values = value.split("..")
        if len(range_values) != 2:
            return EqualExpression(value)
        return RangeExpression(_cast_value(range_values[0]), _cast_value(range_values[1]))

    if "*" in value:
        pattern_values = value.split("*")
        if len(pattern_values) != 2:
            return EqualExpression(value)
        return PatternExpression(pattern_values[0], pattern_values[1])

    if "," in value:
        in_values = value.split(",")
        return InExpression([_cast_value(value.strip()) for value in in_values])

    # fallback to equal
    return EqualExpression(value)
