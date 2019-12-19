from io import BytesIO
from typing import Optional
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

        if body:
            self.write(body)

    @property
    def headers(self):
        return self._headers

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

    def set_cookie(self, cookie: Cookie):
        self.headers.set(*cookie.header())

    def __str__(self):
        self.body.seek(0)
        return self.body.read().decode(self.encoding)


__all__ = ["HttpResponse"]
