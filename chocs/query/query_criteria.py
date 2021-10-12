from typing import List, Dict, Any

from .expression import parse_expression, Expression
from .sorting import parse_sorting

_RESERVED_FIELDS = ("sort", "limit", "order", "cursor", "offset")


class QueryCriteria:
    def __init__(self, query: Dict[str, Any], allowed_fields: List[str] = None):
        self._allowed_fields = allowed_fields
        self.limit = int(query["limit"]) if "limit" in query else 10

        if "cursor" in query:
            self.cursor = query["cursor"]
        else:
            self.offset = int(query["offset"]) if "offset" in query else 0

        self.sort = parse_sorting(query["sort"], allowed_fields) if "sort" in query else {}
        self._fields = create_criteria_fields(query, allowed_fields)

    def items(self):
        return self._fields.items()

    def keys(self):
        return self._fields.keys()

    def values(self):
        return self._fields.values()

    def next_query(self, cursor: str = "") -> str:
        query = [self._base_str]
        if cursor:
            query.append(f"cursor={cursor}")
        else:
            query.append(f"offset={self.offset + self.limit}")

        return "&".join(query)

    def prev_query(self, cursor: str = "") -> str:
        query = [self._base_str]
        if cursor:
            query.append(f"cursor={cursor}")
        elif self.offset - self.limit >= 0:
            query.append(f"offset={self.offset - self.limit}")
        else:
            query.append(f"offset=0")

        return "&".join(query)

    def __contains__(self, name: str) -> bool:
        return self._fields.__contains__(name)

    def __getitem__(self, key: str) -> Expression:
        return self._fields[key]

    def __iter__(self):
        return iter(self.items())

    @property
    def _base_str(self) -> str:
        result = []
        if self._fields:
            result.append("&".join([f"{field}={value}" for field, value in self._fields.items()]))

        if self.sort:
            result.append(",".join([f"{order}{name}" for name, order in self.sort.items()]))

        result.append(f"limit={self.limit}")

        return "&".join(result)

    def __str__(self) -> str:
        query = [self._base_str]

        if hasattr(self, "cursor"):
            query.append(f"cursor={self.cursor}")
        else:
            query.append(f"offset={self.offset}")

        return "&".join(query)

    def __repr__(self):
        return self.__str__()


def create_criteria_fields(query: Dict[str, Any], allowed_fields: List[str] = None) -> Dict[str, Expression]:
    result = {}

    for field, value in query.items():
        if field in _RESERVED_FIELDS:
            continue
        if allowed_fields and field not in allowed_fields:
            continue

        result[field] = parse_expression(value)

    return result


__all__ = ["QueryCriteria", "create_criteria_fields"]
