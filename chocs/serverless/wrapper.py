from typing import Callable

from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse
from chocs.middleware.middleware import MiddlewarePipeline
from chocs.routing import Route
from .aws import AwsServerlessFunction
from .serverless import IS_AWS_ENVIRONMENT, ServerlessFunction
from functools import update_wrapper


def create_serverless_function(
    func: Callable[[HttpRequest], HttpResponse],
    route: Route,
    middleware_pipeline: MiddlewarePipeline,
) -> Callable:

    if IS_AWS_ENVIRONMENT:
        return update_wrapper(AwsServerlessFunction(func, route, middleware_pipeline), func)

    return update_wrapper(ServerlessFunction(func, route, middleware_pipeline), func)


def is_serverless() -> bool:
    if IS_AWS_ENVIRONMENT:
        return True

    return False


__all__ = ["create_serverless_function", "is_serverless"]
