import re
from copy import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Pattern
from typing import Union

_ROUTE_REGEX = r"\\\{\s*(?P<var>[a-z_][a-z0-9_-]*)\s*\\\}"
_VAR_REGEX = "[^/]+"


class Route:
    def __init__(self, route: str, **kwargs):
        self.route = route
        self._part_patterns = kwargs
        self._attribute_names: List[str] = []
        self._pattern: Pattern[str] = None  # type: ignore
        self._attributes: Dict[str, str] = {}
        self.wildcard: bool = "*" in route

    @property
    def pattern(self) -> Pattern[str]:
        if not self._pattern:
            self._parse()
        return self._pattern

    def _parse(self) -> None:
        def _parse_var(match):
            attribute = match.group(1)
            self._attribute_names.append(attribute)
            if attribute in self._part_patterns:
                return f"({self._part_patterns[attribute]})"
            return f"({_VAR_REGEX})"

        pattern = re.escape(self.route)
        pattern = re.sub(_ROUTE_REGEX, _parse_var, pattern, re.I | re.M)
        pattern = re.sub(r"\\\*", ".*?", pattern)
        self._pattern = re.compile("^" + pattern + "$", re.I | re.M,)

    def match(self, uri: str) -> Union[bool, "Route"]:
        matches = self.pattern.findall(uri)
        if not matches:
            return False

        if not self._attribute_names:
            return copy(self)

        if isinstance(matches[0], tuple):
            matches = list(matches[0])

        route = copy(self)
        match_index = 0
        for value in matches:
            route._attributes[self._attribute_names[match_index]] = value
            match_index += 1

        return route

    @property
    def attributes(self):
        return self._attributes

    def __str__(self) -> str:
        return self.route

    def __bool__(self) -> bool:
        return True

    def __getitem__(self, key: str) -> str:
        return self._attributes[key]

    def __contains__(self, key: str) -> bool:
        return key in self._attributes

    def get(self, key: str, default: Optional[Any] = None):
        if key in self:
            return self[key]

        return default


__all__ = ["Route"]
