from io import BytesIO
from typing import Any, Dict

from .http_headers import HttpHeaders
from .http_method import HttpMethod
from .http_query_string import HttpQueryString
from .http_request import HttpRequest


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
