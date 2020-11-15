from typing import Callable
from typing import Dict
from typing import List

from .http_method import HttpMethod
from .routing import Route
from .routing import Router
from .serverless import IS_SERVERLESS_ENVIRONMENT
from .serverless import make_serverless_callback
from .middleware import Middleware


class HttpApplication:
    """
    should support

    schema - for handling json schema
    timeout - for time - outing
    """
    def __init__(self) -> None:
        self.middleware: List[Middleware] = []
        self.methods: Dict[HttpMethod, Router] = {key: Router() for key in HttpMethod}

    def get(self, route: str) -> Callable:
        def _get(handler: Callable) -> Callable:
            self.methods[HttpMethod.GET].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _get

    def post(self, route: str) -> Callable:
        def _post(handler: Callable) -> Callable:
            self.methods[HttpMethod.POST].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _post

    def put(self, route: str) -> Callable:
        def _put(handler: Callable) -> Callable:
            self.methods[HttpMethod.PUT].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _put

    def patch(self, route: str) -> Callable:
        def _patch(handler: Callable) -> Callable:
            self.methods[HttpMethod.PATCH].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _patch

    def delete(self, route: str) -> Callable:
        def _delete(handler: Callable) -> Callable:
            self.methods[HttpMethod.DELETE].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _delete

    def head(self, route: str) -> Callable:
        def _head(handler: Callable) -> Callable:
            self.methods[HttpMethod.HEAD].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _head

    def options(self, route: str) -> Callable:
        def _options(handler: Callable) -> Callable:
            self.methods[HttpMethod.OPTIONS].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _options

    def any(self, route: str) -> Callable:
        def _any(handler: Callable) -> Callable:
            self.methods[HttpMethod.GET].append(Route(route), handler)
            self.methods[HttpMethod.POST].append(Route(route), handler)
            self.methods[HttpMethod.PUT].append(Route(route), handler)
            self.methods[HttpMethod.PATCH].append(Route(route), handler)
            self.methods[HttpMethod.DELETE].append(Route(route), handler)
            self.methods[HttpMethod.HEAD].append(Route(route), handler)
            self.methods[HttpMethod.OPTIONS].append(Route(route), handler)
            if IS_SERVERLESS_ENVIRONMENT:
                return make_serverless_callback(handler, Route(route))
            return handler

        return _any


http = HttpApplication()


__all__ = ["HttpApplication", "http"]
