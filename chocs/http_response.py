import copy
from io import BytesIO
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Union

from .cookie_jar import CookieJar
from .headers import Headers
from .http_status import HttpStatus


class HttpResponse:
    def __init__(
        self,
        status: Union[int, HttpStatus] = HttpStatus.OK,
        body: Union[bytes, bytearray, str, None] = None,
        encoding: str = "utf-8",
        headers: Optional[Union[Dict[str, Union[str, Sequence[str]]], Headers]] = None,
    ):
        self._headers = headers if isinstance(headers, Headers) else Headers(headers)
        self.status_code = status
        self.body = BytesIO()
        self.encoding = encoding
        self.cookies = CookieJar()

        if body:
            self.write(body)

    @property
    def headers(self) -> Headers:
        headers: Headers = copy.copy(self._headers)
        for cookie in self.cookies.values():
            headers.set("Set-Cookie", cookie.serialise())
        return headers

    def write(self, body: Union[str, bytes, bytearray]) -> None:
        if isinstance(body, str):
            self.body.write(body.encode(self.encoding))
        else:
            self.body.write(body)

    @property
    def writable(self) -> bool:
        return not self.body.closed

    def close(self) -> None:
        self.body.close()

    def __str__(self) -> str:
        self.body.seek(0)
        return self.body.read().decode(self.encoding)


__all__ = ["HttpResponse"]
