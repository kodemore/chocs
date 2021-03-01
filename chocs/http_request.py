from copy import copy
from io import BytesIO
from typing import Any, Dict, Optional, Union

from .http_cookies import HttpCookieJar, parse_cookie_header
from .http_headers import HttpHeaders
from .http_method import HttpMethod
from .http_parsed_body import HttpParsedBodyTrait
from .http_query_string import HttpQueryString
from .routing import Route


class HttpRequest(HttpParsedBodyTrait):
    def __init__(
        self,
        method: Union[HttpMethod, str],
        path: str = "/",
        body: Union[Optional[BytesIO], str] = None,
        query_string: Union[Optional[HttpQueryString], str] = None,
        headers: Union[Optional[HttpHeaders], Dict[str, str]] = None,
    ):
        if isinstance(method, str):
            method = HttpMethod(method.upper())

        if isinstance(body, str):
            body = BytesIO(body.encode("utf8"))

        if isinstance(query_string, str):
            query_string = HttpQueryString(query_string)

        if isinstance(headers, dict):
            headers = HttpHeaders(headers)

        self.method = method
        self.path = path
        self.query_string = query_string if query_string else HttpQueryString("")
        self.path_parameters: Dict[str, str] = {}
        self.route: Optional[Route] = None  # type: ignore
        self.attributes: Dict[str, Any] = {}
        self._headers = headers if headers else HttpHeaders()
        self._cookies: Optional[HttpCookieJar] = None
        self._body = body if body else BytesIO(b"")
        self._parsed_body = None
        self._as_dict = None
        self._as_str = None

    @property
    def body(self) -> BytesIO:
        return copy(self._body)

    @property
    def cookies(self) -> HttpCookieJar:
        if self._cookies is None:
            self._cookies = parse_cookie_header(str(self._headers.get("cookie")))

        return copy(self._cookies)

    def __eq__(self, other) -> bool:
        if not isinstance(other, HttpRequest):
            return False

        return (
            self.method == other.method
            and self._headers == other._headers
            and self.path == other.path
            and self.query_string == other.query_string
            and self.body.getbuffer().nbytes == other.body.getbuffer().nbytes
        )

    @property
    def headers(self) -> HttpHeaders:
        return self._headers


__all__ = ["HttpRequest"]
