import os
from copy import copy
from typing import Any
from typing import Callable

from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.middleware import MiddlewareHandler
from chocs.middleware import MiddlewarePipeline
from chocs.routing import Route


class ServerlessFunction:
    route: Route
    middleware_pipeline: MiddlewarePipeline
    function: Callable[[HttpRequest], HttpResponse]

    def __init__(self, function: Callable[[HttpRequest], HttpResponse], route: Route, middleware_pipeline: MiddlewarePipeline):
        self._function = function
        self._route = route
        self._middleware_pipeline = MiddlewarePipeline(middleware_pipeline.queue)
        self._middleware_enabled = False

        def _function_middleware(_request: HttpRequest, _next: MiddlewareHandler) -> HttpResponse:
            _route = copy(route)
            route._parameters = _request.path_parameters
            _request.route = _route

            return function(_request)

        self.middleware_pipeline.append(_function_middleware)

    @property
    def function(self) -> Callable[[HttpRequest], HttpResponse]:
        return self._function

    @property
    def route(self) -> Route:
        return self._route

    @property
    def middleware_pipeline(self) -> MiddlewarePipeline:
        return self._middleware_pipeline

    @property
    def middleware_enabled(self) -> bool:
        return self._middleware_enabled

    @middleware_enabled.setter
    def middleware_enabled(self, value: bool) -> None:
        self._middleware_enabled = value

    def __call__(self, *args, **kwargs) -> Any:
        if self._middleware_enabled and not self._middleware_pipeline.empty:
            return self._middleware_pipeline(*args, **kwargs)

        return self._function(*args, **kwargs)


IS_AWS_ENVIRONMENT = bool(
    os.environ.get("AWS_LAMBDA_FUNCTION_VERSION")
    or os.environ.get("LAMBDA_RUNTIME_DIR")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
)


__all__ = ['ServerlessFunction', 'IS_AWS_ENVIRONMENT']