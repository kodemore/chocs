from io import BytesIO
from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from . import HttpResponse
from .application import http
from .http_error import HttpError
from .http_headers import HttpHeaders
from .http_method import HttpMethod
from .http_query_string import HttpQueryString
from .http_request import HttpRequest
from .middleware import Middleware
from .middleware import MiddlewarePipeline
from .router_middleware import RouterMiddleware


def create_http_request_from_wsgi(environ: Dict[str, Any]) -> HttpRequest:
    headers = HttpHeaders()
    for key, value in environ.items():
        if not key.startswith("HTTP"):
            continue
        headers.set(key, value)
    headers.set("Content-Type", environ.get("CONTENT_TYPE", "text/plain"))

    return HttpRequest(
        method=HttpMethod(environ.get("REQUEST_METHOD", "GET").upper()),
        path=environ.get("PATH_INFO", "/"),
        body=environ.get("wsgi.input", BytesIO(b"")),
        query_string=HttpQueryString(environ.get("QUERY_STRING", "")),
        headers=headers,
    )


def create_wsgi_handler(debug: bool = False, middleware: List[Middleware] = http.middleware) -> Callable[[Dict[str, Any]], Callable]:

    def _handler(environ: Dict[str, Any], start: Callable) -> Any:
        # Prepare pipeline
        middleware_pipeline = MiddlewarePipeline()
        for item in middleware:
            middleware_pipeline.append(item)

        middleware_pipeline.append(RouterMiddleware.from_http_application(http))

        request = create_http_request_from_wsgi(environ)

        if debug:
            try:
                response = middleware_pipeline(request)
            except HttpError as http_error:
                response = HttpResponse(http_error.status_code, http_error.http_message)
        else:
            # Always send a response
            try:
                response = middleware_pipeline(request)
            except HttpError as http_error:
                response = HttpResponse(http_error.status_code, http_error.http_message)
            except Exception:
                response = HttpResponse(500, "Internal Server Error")

        start(
            str(response.status_code),
            [(key, value) for key, value in response.headers.items()],
        )

        response.body.seek(0)
        return response.body

    return _handler
