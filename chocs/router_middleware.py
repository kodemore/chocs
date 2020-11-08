from typing import Callable
from typing import Dict

from .http_error import HttpError
from .http_method import HttpMethod
from .http_request import HttpRequest
from .http_response import HttpResponse
from .middleware import Middleware
from .middleware import MiddlewareHandler
from .routing import Route
from .routing import Router
from .application import HttpApplication


class RouterMiddleware(Middleware):
    def __init__(self):
        self.methods: Dict[HttpMethod, Router] = {key: Router() for key in HttpMethod}

    @classmethod
    def from_http_application(cls, http_application: HttpApplication) -> "RouterMiddleware":
        instance = cls()
        instance.methods = http_application.methods

        return instance

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        try:
            route, controller = self.methods[request.method].match(
                request.path
            )  # type: Route, Callable

            request.path_parameters = route.parameters
            request.route = route
            response: HttpResponse = controller(request)

            return response
        except HttpError as error:
            return HttpResponse(status=error.status_code, body=error.http_message)


__all__ = ["RouterMiddleware"]
