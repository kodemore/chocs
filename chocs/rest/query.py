from abc import ABC
from collections import UserDict
from enum import Enum
from typing import List, Union, Dict, Set
from chocs.http.http_query_string import HttpQueryString

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

    def __init__(self, field: str, value: ExpressionValue):
        self.field = field
        self.value = value

    def __str__(self) -> str:
        return f"{self.field}={self.value}"


class GreaterThanExpression(Expression):
    value: ExpressionValue

    def __init__(self, field: str, value: ExpressionValue):
        self.field = field
        self.value = value

    def __str__(self) -> str:
        return f"{self.field}=>{self.value}"


class LowerThanExpression(Expression):
    value: ExpressionValue

    def __init__(self, field: str, value: ExpressionValue):
        self.field = field
        self.value = value

    def __str__(self) -> str:
        return f"{self.field}=<{self.value}"


class RangeExpression(Expression):
    start: ExpressionValue
    end: ExpressionValue

    def __init__(self, field: str, start: ExpressionValue, end: ExpressionValue):
        self.field = field
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.field}={self.start}..{self.end}"


class PatternExpression(Expression):
    start: ExpressionValue
    end: ExpressionValue

    def __init__(self, field: str, start: str, end: str):
        self.field = field
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.field}={self.start}*{self.end}"


class InExpression(Expression):
    values: List[ExpressionValue]

    def __init__(self, field: str, values: List[ExpressionValue]):
        self.field = field
        self.values = values

    def __str__(self) -> str:
        result = []
        for value in self.values:
            result.append(f"{self.field}[]={value}")

        return "&".join(result)


class SortDirection(Enum):
    ASCENDING = 1
    DESCENDING = -1

    def __str__(self):
        if self.value == -1:
            return "-"
        return "+"


class SortOrder(UserDict):
    def __str__(self) -> str:
        return ",".join([f"{order}{name}" for name, order in self.data.items()])

    def is_empty(self) -> bool:
        return len(self) == 0


class FilteringFields(UserDict):
    def __str__(self) -> str:
        return "&".join([f"{field}" for field in self.data.values()])

    def is_empty(self) -> bool:
        return len(self) == 0


def create_expression(field: str, value: Union[list, str]) -> Expression:
    if isinstance(value, list):
        return InExpression(field, value)

    if value in ("..", ">", "<", "*"):
        return EqualExpression(field, value)

    if value.startswith(">"):
        return GreaterThanExpression(field, _cast_value(value[1:]))

    if value.startswith("<"):
        return LowerThanExpression(field, _cast_value(value[1:]))

    if ".." in value:
        range_values = value.split("..")
        if len(range_values) != 2:
            return EqualExpression(field, value)
        return RangeExpression(field, _cast_value(range_values[0]), _cast_value(range_values[1]))

    if "*" in value:
        pattern_values = value.split("*")
        if len(pattern_values) != 2:
            return EqualExpression(field, value)
        return PatternExpression(field, pattern_values[0], pattern_values[1])

    return EqualExpression(field, value)


def create_sort_order(value: str, allowed_fields: List[str]) -> SortOrder:
    fields = value.split(",")
    result = SortOrder()
    allowed_fields = set(allowed_fields)

    for field in fields:
        field = field.strip()
        if field.startswith("-"):
            field_name = field[1:]
            direction = SortDirection.DESCENDING
        elif field.startswith("+"):
            field_name = field[1:]
            direction = SortDirection.ASCENDING
        else:
            field_name = field
            direction = SortDirection.ASCENDING

        if field_name not in allowed_fields:
            continue

        result[field_name] = direction

    return result


def create_filtering_fields(query_string: HttpQueryString, allowed_fields: List[str]) -> FilteringFields:
    allowed_fields = set(allowed_fields)
    result = FilteringFields()

    for field, value in query_string.items():
        if field not in allowed_fields:
            continue

        result[field] = create_expression(field, value)

    return result


class Query:
    def __init__(self, query_string: HttpQueryString, allowed_fields: List[str]):
        self._allowed_fields = allowed_fields
        self.limit = int(query_string["limit"]) if "limit" in query_string else 10

        if "cursor" in query_string:
            self.cursor = query_string["cursor"]
        else:
            self.offset = int(query_string["offset"]) if "offset" in query_string else 0

        self.sort = create_sort_order(query_string["sort"], allowed_fields) if "sort" in query_string else None
        self.fields = create_filtering_fields(query_string, allowed_fields)

    def _page_attributes(self) -> List[str]:
        result = []
        if not self.fields.is_empty():
            result.append(str(self.fields))

        if not self.sort.is_empty():
            result.append(str(self.fields))

        result.append(f"limit={self.limit}")

        return result

    def next_page(self, cursor: str = "") -> str:
        result = self._page_attributes()

        if hasattr(self, "offset"):
            result.append(f"offset={self.offset + self.limit}")
        else:
            result.append(f"cursor={cursor}")

        return "&".join(result)

    def prev_page(self, cursor: str = "") -> str:
        result = self._page_attributes()

        if hasattr(self, "offset"):
            value = self.offset - self.limit
            if value > 0:
                result.append(f"offset={self.offset - self.limit}")
            else:
                result.append("offset=0")
        else:
            result.append(f"cursor={cursor}")

        return "&".join(result)
