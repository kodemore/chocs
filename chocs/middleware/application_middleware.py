from chocs.http.http_error import HttpError
from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse
from chocs.routing import Router
from chocs.serverless.serverless import ServerlessFunction

from .middleware import Middleware, MiddlewareHandler


class ApplicationMiddleware(Middleware):
    def __init__(self, router: Router):
        self.router = router

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        try:
            handler = request.attributes["__handler__"]

            response: HttpResponse
            if isinstance(handler, ServerlessFunction):
                response = handler.function(request)
            else:
                response = handler(request)

            return response
        except HttpError as error:
            return HttpResponse(status=error.status_code, body=error.http_message)


__all__ = ["ApplicationMiddleware"]
