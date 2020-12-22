from chocs import Application, HttpRequest, HttpResponse
from chocs.middleware import Middleware, MiddlewareHandler


def cors_middleware(request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
    response = next(request)
    response._headers.set('Access-Control-Allow-Origin', '*')

    return response


class CorsMiddleware(Middleware):
    def __init__(self, allowed_access_from: str):
        self.cors = allowed_access_from

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:

        response = next(request)
        response._headers.set('Access-Control-Allow-Origin', self.cors)

        return response


app = Application(CorsMiddleware('*'))
