from cgi import parse_header
from io import BytesIO
from copy import copy
from typing import Dict, Optional, Tuple, Union, Any

from .http_cookies import HttpCookieJar, parse_cookie_header
from .http_headers import HttpHeaders
from .http_message import HttpMessage, FormHttpMessage, JsonHttpMessage, MultipartHttpMessage
from .http_method import HttpMethod
from .http_query_string import HttpQueryString


class HttpRequest:
    def __init__(
        self,
        method: Union[HttpMethod, str],
        path: str = "/",
        body: Union[Optional[BytesIO], str] = None,
        query_string: Union[Optional[HttpQueryString], str] = None,
        headers: Union[Optional[HttpHeaders], Dict[str, str]] = None,
    ):
        if isinstance(method, str):
            method = HttpMethod(method)

        if isinstance(body, str):
            body = BytesIO(body.encode("utf8"))

        if isinstance(query_string, str):
            query_string = HttpQueryString(query_string)

        if isinstance(headers, dict):
            headers = HttpHeaders(headers)

        self.method = method
        self.path = path
        self.query_string = query_string
        self.path_parameters: Dict[str, str] = {}
        self.headers = headers if headers else HttpHeaders()

        self._body = body if body else BytesIO(b"")
        self._parsed_body: Optional[HttpMessage] = None
        self._cookies: Optional[HttpCookieJar] = None

    @property
    def body(self) -> BytesIO:
        return copy(self._body)

    @property
    def parsed_body(self) -> HttpMessage:
        if self._parsed_body:
            return copy(self._parsed_body)

        content_type: Tuple[str, Dict[str, str]] = parse_header(
            self.headers["Content-Type"]  # type: ignore
        )

        if content_type[0] == "multipart/form-data":
            parsed_body = MultipartHttpMessage.from_bytes(
                self.body,
                content_type[1].get("charset", ""),
                content_type[1].get("boundary", ""),
            )
        elif content_type[0] == "application/x-www-form-urlencoded":
            parsed_body = FormHttpMessage.from_bytes(
                self.body,
                content_type[1].get("charset", "utf8")
            )

        elif content_type[0] == "application/json":
            parsed_body = JsonHttpMessage.from_bytes(
                self.body,
                content_type[1].get("charset", "utf8")
            )
        else:
            self.body.seek(0)
            parsed_body = self.body.read().decode(content_type[1].get("charset", "utf8"))

        self._parsed_body = parsed_body

        return copy(self._parsed_body)

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = parse_cookie_header(self.headers.get("cookie"))

        return copy(self._cookies)


__all__ = ["HttpRequest"]
