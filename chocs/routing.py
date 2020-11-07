import re
from copy import copy
from typing import Any, Dict, Optional, Pattern, Union
from typing import Callable, List, Tuple

from .http_error import NotFoundError

_ROUTE_REGEX = r"\\\{\s*(?P<var>[a-z_][a-z0-9_-]*)\s*\\\}"
_VAR_REGEX = "[^/]+"


class Route:
    def __init__(self, route: str):
        self.route = route
        self._parameters_names: List[str] = []
        self._pattern: Pattern[str] = None  # type: ignore
        self._parameters: Dict[str, str] = {}
        self.is_wildcard: bool = "*" in route

    @property
    def pattern(self) -> Pattern[str]:
        if not self._pattern:
            self._parse()
        return self._pattern

    def _parse(self) -> None:
        def _parse_var(match):
            param = match.group(1)
            self._parameters_names.append(param)
            return f"({_VAR_REGEX})"

        pattern = re.escape(self.route)
        pattern = re.sub(_ROUTE_REGEX, _parse_var, pattern, re.I | re.M)
        pattern = re.sub(r"\\\*", ".*?", pattern)
        self._pattern = re.compile("^" + pattern + "$", re.I | re.M,)

    def match(self, uri: str) -> Union[bool, "Route"]:
        matches = self.pattern.findall(uri)
        if not matches:
            return False

        if not self._parameters_names:
            return copy(self)

        if isinstance(matches[0], tuple):
            matches = list(matches[0])

        route = copy(self)
        match_index = 0
        for value in matches:
            route._parameters[self._parameters_names[match_index]] = value
            match_index += 1

        return route

    @property
    def parameters(self):
        return self._parameters

    def __str__(self) -> str:
        return self.route

    def __bool__(self) -> bool:
        return True

    def __getitem__(self, key: str) -> str:
        return self._parameters[key]

    def __contains__(self, key: str) -> bool:
        return key in self._parameters

    def get(self, key: str, default: Optional[Any] = None):
        if key in self:
            return self[key]

        return default


class Router:
    def __init__(self):
        self._routes: List[Tuple[Route, Callable]] = []

    def append(self, route: Route, handler: Callable) -> None:
        assert isinstance(route, Route), "Passed route must be instance of Route"

        self._routes.append((route, handler))
        self._routes.sort(key=lambda r: r[0].is_wildcard)

    def match(self, uri: str) -> Tuple[Route, Callable]:
        for route in self._routes:
            if route[0].match(uri):
                return route

        raise NotFoundError(f"Could not match any resource matching {uri} uri")


__all__ = ["Route", "Router"]
