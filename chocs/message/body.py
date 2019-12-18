from collections import UserDict
from typing import Any
from typing import Optional


class RequestBody(UserDict):
    def get(self, name: str, default: Optional[Any] = None) -> Any:
        if name in self:
            return self[name]

        return default


__all__ = ["RequestBody"]
