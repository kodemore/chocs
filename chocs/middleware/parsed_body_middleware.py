import inspect
from typing import Any

from chocs.dataclasses.support import init_dataclass, is_dataclass
from chocs.http_message import CompositeHttpMessage
from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.middleware import Middleware, MiddlewareHandler
from chocs.routing import Route


class ParsedBodyMiddleware(Middleware):
    def __init__(self, strict: bool = True):
        self.strict = strict

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        route = request.route
        assert isinstance(route, Route)
        if "parsed_body" in route.attributes:
            self._map_parsed_body(request, route)

        return next(request)

    def _map_parsed_body(self, request: HttpRequest, route: Route) -> None:
        if not inspect.isclass(route.attributes["parsed_body"]):
            return

        if not isinstance(request.parsed_body, CompositeHttpMessage):
            return

        body = request.parsed_body

        strict = route.attributes["strict"] if "strict" in route.attributes else self.strict
        constructor = route.attributes["parsed_body"]
        request._parsed_body = None

        if not strict:

            def _get_non_strict_parsed_body() -> Any:
                if not is_dataclass(constructor):
                    raise ValueError(
                        f"parsed_body argument expects valid dataclass type to be passed, {constructor} was given."
                    )
                return init_dataclass(body, constructor)  # type: ignore

            request._parsed_body_getter = _get_non_strict_parsed_body

            return

        def _get_strict_parsed_body() -> Any:
            return constructor(**body)

        request._parsed_body_getter = _get_strict_parsed_body


__all__ = ["ParsedBodyMiddleware"]
