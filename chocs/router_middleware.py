from typing import Callable, Union

from .http_error import HttpError
from .http_request import HttpRequest
from .http_response import HttpResponse
from .middleware import Middleware, MiddlewareHandler
from .routing import Route, Router
from .serverless.serverless import ServerlessFunction


class RouterMiddleware(Middleware):
    def __init__(self, router: Router):
        self.router = router

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        try:
            route, controller = self.router.match(
                request.path, request.method
            )  # type: Route, Union[Callable, ServerlessFunction]

            request.path_parameters = route.parameters
            request.route = route

            response: HttpResponse
            if isinstance(controller, ServerlessFunction):
                response = controller.function(request)
            else:
                response = controller(request)

            return response
        except HttpError as error:
            return HttpResponse(status=error.status_code, body=error.http_message)


__all__ = ["RouterMiddleware"]
