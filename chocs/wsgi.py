from io import BytesIO
from typing import Any, Callable, Dict

from .application import Application
from .http_error import HttpError
from .http_headers import HttpHeaders
from .http_method import HttpMethod
from .http_query_string import HttpQueryString
from .http_request import HttpRequest
from .http_response import HttpResponse
import gunicorn.app.base


class ChocsGunicornApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app: Callable, options: Dict[str, Any] = None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self) -> None:
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Any:
        return self.application


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


def serve(application: Application, host: str = "127.0.0.1", port: int = 80, workers: int = 1, reload: bool = True, debug: bool = False) -> None:

    wsgi_handler = create_wsgi_handler(application, debug=debug)
    options = {
        "bind": f"{host}:{port}",
        "workers": workers,
        "reload": reload
    }

    server = ChocsGunicornApplication(wsgi_handler, options)
    server.run()
