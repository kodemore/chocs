from io import BytesIO
from typing import Callable

from chocs import HttpMethod
from chocs import HttpRequest
from chocs import HttpResponse
from chocs.wsgi import create_wsgi_handler


def test_create_wsgi_handler() -> None:
    def _http_start(status_code, headers):
        assert status_code == "200"

    def _serve_response(request: HttpRequest, next: Callable) -> HttpResponse:
        assert request.method == HttpMethod.POST
        return HttpResponse("OK")

    handler = create_wsgi_handler(_serve_response)

    handler({
        "CONTENT_TYPE": "text/plain",
        "REQUEST_METHOD": "POST",
        "wsgi.input": BytesIO(b"Test input"),
    }, _http_start)


