from io import BytesIO
from typing import Any, Callable, Dict

from .application import Application
from .http_error import HttpError
from .http_headers import HttpHeaders
from .http_method import HttpMethod
from .http_query_string import HttpQueryString
from .http_request import HttpRequest
from .http_response import HttpResponse


def create_http_request_from_wsgi(environ: Dict[str, Any]) -> HttpRequest:
    headers = HttpHeaders()
    for key, value in environ.items():
        if not key.startswith("HTTP"):
            continue
        headers.set(key, value)
    headers.set("Content-Type", environ.get("CONTENT_TYPE", "text/plain"))

    if "wsgi.input" in environ:  # unify all the different types of wsgi server implementations
        body = BytesIO(environ["wsgi.input"].read())
    else:
        body = BytesIO(b"")

    return HttpRequest(
        method=HttpMethod(environ.get("REQUEST_METHOD", "GET").upper()),
        path=environ.get("PATH_INFO", "/"),
        body=body,
        query_string=HttpQueryString(environ.get("QUERY_STRING", "")),
        headers=headers,
    )


def create_wsgi_handler(
    application: Application, debug: bool = False
) -> Callable[[Dict[str, Any], Callable[..., Any]], BytesIO]:
    def _handler(environ: Dict[str, Any], start: Callable) -> BytesIO:
        request = create_http_request_from_wsgi(environ)
        if debug:
            try:
                response = application(request)
            except HttpError as http_error:
                response = HttpResponse(http_error.http_message, http_error.status_code)
        else:
            # Always send a response
            try:
                response = application(request)
            except HttpError as http_error:
                response = HttpResponse(http_error.http_message, http_error.status_code)
            except Exception:
                response = HttpResponse("Internal Server Error", 500)

        headers = response.headers
        for cookie in response.cookies.values():
            headers.set("Set-Cookie", cookie.serialise())

        start(
            str(int(response.status_code)),
            [(key, value) for key, value in headers.items()],
        )

        response.body.seek(0)
        return response.body

    return _handler


def serve(application: Application, host: str = "127.0.0.1", port: int = 80, debug: bool = False) -> None:
    import bjoern

    wsgi_handler = create_wsgi_handler(application, debug=debug)

    bjoern.run(wsgi_handler, host, port)
