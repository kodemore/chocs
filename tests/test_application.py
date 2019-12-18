from io import BytesIO
from typing import Callable

from chocs import Application
from chocs import HttpRequest
from chocs import HttpResponse
from chocs.middleware import Middleware
from chocs.middleware import MiddlewareHandler
from chocs.middleware import MiddlewarePipeline


class RespondingMiddleware(Middleware):
    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        response = HttpResponse(200)
        response.write("OK")
        return response


def test_can_instantiate():
    app = Application()


def test_can_run():
    def _app_runner(handler: Callable, host: str, port: int):
        def _http_start(status_code, headers):
            assert status_code == "200"

        assert isinstance(handler, Application)
        assert host == "0.0.0.0"
        assert port == 80
        response = handler(
            {
                "CONTENT_TYPE": "text/plain",
                "REQUEST_METHOD": "POST",
                "wsgi.input": BytesIO(b"Test input"),
            },
            _http_start,
        )

        assert response.read() == b"OK"

    app = Application()

    assert isinstance(app.middleware, MiddlewarePipeline)
