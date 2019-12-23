from cgi import parse_header
from io import BytesIO
from typing import Any
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union

from .cookie_jar import CookieJar
from .cookie_jar import parse_cookie_header
from .headers import Headers
from .http_method import HttpMethod
from .message.body import RequestBody
from .message.form_body import FormBody
from .message.json_body import JsonBody
from .message.multipart_body import MultipartBody
from .query_string import QueryString


class HttpRequest:
    def __init__(
        self,
        method: HttpMethod,
        uri: str = "/",
        body: Optional[BytesIO] = None,
        query_string: Optional[QueryString] = None,
        headers: Optional[Headers] = None,
    ):
        self.headers = headers if headers else Headers()
        self.body = body if body else BytesIO(b"")
        self.method = method
        self.uri = uri
        self.query_string = query_string
        self._parsed_body: Union[RequestBody, str] = ""
        self.attributes: Dict[str, str] = {}
        self._cookies: Optional[CookieJar] = None

    @property
    def parsed_body(self) -> Union[RequestBody, str]:
        if self._parsed_body:
            return self._parsed_body

        content_type: Tuple[str, Dict[str, str]] = parse_header(
            self.headers.get("Content-Type")  # type: ignore
        )

        if content_type[0] == "multipart/form-data":
            body: Union[RequestBody, str] = MultipartBody.from_wsgi(
                self.body,
                content_type[1].get("charset", ""),
                content_type[1].get("boundary", ""),
            )
        elif content_type[0] == "application/x-www-form-urlencoded":
            body = FormBody.from_wsgi(self.body, content_type[1].get("charset", ""))

        elif content_type[0] == "application/json":
            body = JsonBody.from_wsgi(self.body, content_type[1].get("charset", ""))
        else:
            self.body.seek(0)
            body = self.body.read().decode(content_type[1].get("charset", ""))

        self._parsed_body = body

        return self._parsed_body

    @classmethod
    def from_wsgi(cls, environ: Dict[str, Any]) -> "HttpRequest":
        headers = Headers()
        for key, value in environ.items():
            if not key.startswith("HTTP"):
                continue
            headers.set(key, value)
        headers.set("Content-Type", environ.get("CONTENT_TYPE", "text/plain"))
        return cls(
            method=HttpMethod(environ.get("REQUEST_METHOD", "GET").upper()),
            uri=environ.get("PATH_INFO", "/"),
            body=environ.get("wsgi.input", BytesIO(b"")),
            query_string=QueryString(environ.get("QUERY_STRING", "")),
            headers=headers,
        )

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = parse_cookie_header(self.headers.get("cookie"))

        return self._cookies


__all__ = ["HttpRequest"]
