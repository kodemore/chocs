from __future__ import annotations

from copy import copy, deepcopy
from io import BytesIO
from typing import Any, Dict, Optional, Union

from chocs.routing import Route
from .http_body import write_body
from .http_cookies import HttpCookieJar, parse_cookie_header
from .http_headers import HttpHeaders
from .http_method import HttpMethod
from .http_parsed_body import HttpParsedBodyTrait
from .http_query_string import HttpQueryString


class HttpRequest(HttpParsedBodyTrait):
    def __init__(
        self,
        method: Union[HttpMethod, str],
        path: str = "/",
        body: Union[BytesIO, bytes, bytearray, str, None] = None,
        query_string: Union[Optional[HttpQueryString], str] = None,
        headers: Union[Optional[HttpHeaders], Dict[str, str]] = None,
        encoding: str = "utf-8",
    ):
        if isinstance(method, str):
            method = HttpMethod(method.upper())

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
        self.encoding = encoding
        self._headers = headers if headers else HttpHeaders()
        self._cookies: Optional[HttpCookieJar] = None
        self._body = BytesIO()
        self._parsed_body = None
        self._as_dict = None
        self._as_str = None

        if body:
            write_body(self._body, body, encoding)

    @property
    def body(self) -> BytesIO:
        return self._body

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

    def __str__(self) -> str:
        self._body.seek(0)
        return self._body.read().decode(self.encoding)

    def __copy__(self) -> HttpRequest:
        new_copy = HttpRequest.__new__(HttpRequest)
        new_copy.method = self.method
        new_copy.path = self.path
        new_copy.query_string = deepcopy(self.query_string)
        new_copy._headers = copy(self._headers)
        new_copy._cookies = None  # reset cookies after copy
        self._body.seek(0)
        new_copy._body = BytesIO(self._body.read())
        new_copy.path_parameters = {key: value for key, value in self.path_parameters.items()}
        new_copy.attributes = {key: value for key, value in self.attributes.items()}

        return new_copy

    @property
    def headers(self) -> HttpHeaders:
        return self._headers


__all__ = ["HttpRequest"]
