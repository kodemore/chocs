from typing import Callable

from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse
from chocs.middleware.middleware import MiddlewarePipeline
from chocs.routing import Route
from .aws import AwsServerlessFunction
from .serverless import IS_AWS_ENVIRONMENT, ServerlessFunction


def create_serverless_function(
    func: Callable[[HttpRequest], HttpResponse],
    route: Route,
    middleware_pipeline: MiddlewarePipeline,
) -> Callable:

    if IS_AWS_ENVIRONMENT:
        return AwsServerlessFunction(func, route, middleware_pipeline)

    return ServerlessFunction(func, route, middleware_pipeline)


__all__ = ["create_serverless_function"]
