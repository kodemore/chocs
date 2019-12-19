import copy
from io import BytesIO
from typing import Optional, List
from typing import Union

from cookies import Cookie
from .headers import Headers
from .http_status import HttpStatus


class HttpResponse:
    def __init__(
        self,
        status: Union[int, HttpStatus] = HttpStatus.OK,
        body: Union[bytes, bytearray, str, None] = None,
        encoding: str = "utf-8",
        headers: Optional[Union[dict, Headers]] = None,
    ):
        self._headers = headers if isinstance(headers, Headers) else Headers(headers)
        self.status_code = status
        self.body = BytesIO()
        self.encoding = encoding
        self.cookies: List[Cookie] = []

        if body:
            self.write(body)

    @property
    def headers(self):
        headers: Headers = copy.copy(self._headers)
        for cookie in self.cookies:
            headers.set(*cookie.header())
        return headers

    def write(self, body: Union[str, bytes, bytearray]) -> None:
        if isinstance(body, str):
            self.body.write(body.encode(self.encoding))
        else:
            self.body.write(body)

    @property
    def writable(self):
        return not self.body.closed

    def close(self):
        self.body.close()

    def __str__(self):
        self.body.seek(0)
        return self.body.read().decode(self.encoding)


__all__ = ["HttpResponse"]
