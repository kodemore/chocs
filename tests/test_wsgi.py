from io import BytesIO
from typing import Callable

from chocs import Application, HttpCookie, HttpMethod, HttpRequest, HttpResponse
from chocs.wsgi import create_wsgi_handler


def test_create_wsgi_handler() -> None:
    def _http_start(status_code, headers):
        assert headers == [
            ("content-type", "text/plain"),
        ]
        assert status_code == "200"

    def _serve_response(request: HttpRequest, next: Callable) -> HttpResponse:
        assert request.method == HttpMethod.POST
        return HttpResponse("OK", headers=request.headers)

    app = Application(_serve_response)
    handler = create_wsgi_handler(app)

    handler(
        {
            "CONTENT_TYPE": "text/plain",
            "REQUEST_METHOD": "POST",
            "wsgi.input": BytesIO(b"Test input"),
        },
        _http_start,
    )


def test_handling_cookies_by_wsgi_handler() -> None:
    def _http_start(status_code, headers):
        assert headers == [
            ("content-type", "text/plain"),
            ("set-cookie", "test=SuperCookie")
        ]
        assert status_code == "200"

    def _serve_response(request: HttpRequest, next: Callable) -> HttpResponse:
        assert request.method == HttpMethod.POST
        response = HttpResponse("OK", headers=request.headers)
        response.cookies.append(HttpCookie(name="test", value="SuperCookie"))

        return response

    app = Application(_serve_response)
    handler = create_wsgi_handler(app)

    handler(
        {
            "CONTENT_TYPE": "text/plain",
            "REQUEST_METHOD": "POST",
            "wsgi.input": BytesIO(b"Test input"),
        },
        _http_start,
    )
