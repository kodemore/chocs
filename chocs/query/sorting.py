from enum import Enum
from typing import List, Dict


class SortDirection(Enum):
    ASCENDING = 1
    DESCENDING = -1

    def __str__(self) -> str:
        if self.value == -1:
            return "-"
        return "+"


def parse_sorting(value: str, allowed_fields: List[str] = None) -> Dict[str, SortDirection]:
    fields = value.split(",")
    result = {}

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

        if allowed_fields and field_name not in allowed_fields:
            continue

        result[field_name] = direction

    return result
