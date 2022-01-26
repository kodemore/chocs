import os
from typing import Any

from chocs.middleware.middleware import MiddlewarePipeline
from chocs.routing import Route
from chocs.types import HttpHandlerFunction


class ServerlessFunction:
    def __init__(
        self,
        function: HttpHandlerFunction,
        route: Route = Route("/"),
        middleware_pipeline: MiddlewarePipeline = MiddlewarePipeline(),
    ):
        self._function = function
        self._route = route
        self._middleware_pipeline = MiddlewarePipeline(middleware_pipeline.queue)
        self._middleware_enabled = False

    @property
    def function(self) -> HttpHandlerFunction:
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

    def __call__(self, *args) -> Any:
        if self._middleware_enabled and not self._middleware_pipeline.empty:
            return self._middleware_pipeline(*args)

        return self._function(*args)


IS_AWS_ENVIRONMENT = bool(
    os.environ.get("AWS_LAMBDA_FUNCTION_VERSION")
    or os.environ.get("LAMBDA_RUNTIME_DIR")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
)


__all__ = ["ServerlessFunction", "IS_AWS_ENVIRONMENT"]
