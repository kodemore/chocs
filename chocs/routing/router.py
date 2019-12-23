from typing import Callable
from typing import List
from typing import Tuple

from chocs.errors.not_found_error import NotFoundError
from .route import Route


class Router:
    def __init__(self):
        self._routes: List[Tuple[Route, Callable]] = []

    def append(self, route: Route, handler: Callable) -> None:
        assert isinstance(route, Route), "Passed route must be instance of Route"

        self._routes.append((route, handler))
        self._routes.sort(key=lambda r: r[0].wildcard)

    def match(self, uri: str) -> Tuple[Route, Callable]:
        for route in self._routes:
            if route[0].match(uri):
                return route

        raise NotFoundError(f"Could not match any resource matching {uri} uri")


__all__ = ["Router"]
