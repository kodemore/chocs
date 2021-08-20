import re
from copy import copy
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union

from chocs.http.http_error import NotFoundError
from chocs.http.http_method import HttpMethod
from chocs.http.http_query_string import parse_qs_value

_ROUTE_REGEX = r"\\\{\s*(?P<var>[a-z_][a-z0-9_-]*)\s*\\\}"
_VAR_REGEX = "[^/]+"


class Route:
    __slots__ = [
        "route",
        "attributes",
        "_parameters_names",
        "_pattern",
        "_parameters",
        "is_wildcard",
    ]

    def __init__(self, route: str, attributes: Optional[Dict] = None):
        self.route = route
        self.attributes = attributes if attributes is not None else {}
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
        self._pattern = re.compile(
            "^" + pattern + "$",
            re.I | re.M,
        )

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
            route._parameters[self._parameters_names[match_index]] = parse_qs_value(value)
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
        self._routes: Dict[HttpMethod, List[Tuple[Route, Callable]]] = {}

    def append(
        self,
        route: Route,
        handler: Callable,
        methods: Union[str, HttpMethod, List[Union[str, HttpMethod]]] = HttpMethod.GET,
    ) -> None:
        assert isinstance(route, Route), "Passed route must be instance of Route"
        normalised_methods = self._normalise_methods(methods)

        for method in normalised_methods:
            if method not in self._routes:
                self._routes[method] = []

            self._routes[method].append((route, handler))
            self._routes[method].sort(key=lambda r: r[0].is_wildcard)

    @staticmethod
    def _normalise_methods(methods: Union[str, HttpMethod, List[Union[str, HttpMethod]]]) -> List[HttpMethod]:
        if methods == "*":
            methods = [method for method in HttpMethod]
        elif isinstance(methods, HttpMethod):
            methods = [methods]
        else:
            methods = [method if isinstance(method, HttpMethod) else HttpMethod(method.upper()) for method in methods]

        return methods  # type: ignore

    def match(self, uri: str, method: Union[HttpMethod, str] = HttpMethod.GET) -> Tuple[Route, Callable]:
        if isinstance(method, str):
            method = HttpMethod(method)

        if method not in self._routes:
            raise NotFoundError(f"Could not match any resource matching {method} {uri} uri")

        for route in self._routes[method]:
            if route[0].match(uri):
                return route

        raise NotFoundError(f"Could not match any resource matching {method} {uri} uri")


__all__ = ["Route", "Router"]
