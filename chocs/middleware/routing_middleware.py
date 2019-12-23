from typing import Callable
from typing import Dict

from chocs.errors import HttpError
from chocs.http_method import HttpMethod
from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.middleware import Middleware
from chocs.middleware.middleware_handler import MiddlewareHandler
from chocs.routing.route import Route
from chocs.routing.router import Router


class RoutingMiddleware(Middleware):
    def __init__(self) -> None:
        self.methods: Dict[HttpMethod, Router] = {key: Router() for key in HttpMethod}

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        try:
            route, controller = self.methods[request.method].match(
                request.uri
            )  # type: Route, Callable

            request.attributes = route.attributes
            response: HttpResponse = controller(request)

            return response
        except HttpError as error:
            return HttpResponse(status=error.status_code, body=error.http_message)


__all__ = ["RoutingMiddleware"]
