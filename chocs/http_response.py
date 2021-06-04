from io import BytesIO
from typing import Dict, Optional, Sequence, Union

from .http_body import write_body
from .http_cookies import HttpCookieJar
from .http_headers import HttpHeaders
from .http_parsed_body import HttpParsedBodyTrait
from .http_status import HttpStatus


class HttpResponse(HttpParsedBodyTrait):
    def __init__(
        self,
        body: Union[BytesIO, bytes, bytearray, str, None] = None,
        status: Union[int, HttpStatus] = HttpStatus.OK,
        headers: Optional[Union[Dict[str, Union[str, Sequence[str]]], HttpHeaders]] = None,
        encoding: str = "utf-8",
    ):
        self._headers = headers if isinstance(headers, HttpHeaders) else HttpHeaders(headers)
        if isinstance(status, int):
            status = HttpStatus.from_int(status)
        self.status_code = status
        self._body: BytesIO = BytesIO()
        self.encoding = encoding
        self.cookies = HttpCookieJar()
        self._parsed_body = None
        self._as_dict = None
        self._as_str = None

        if body:
            self.write(body)

    def write(self, body: Union[str, bytes, bytearray, BytesIO]) -> None:
        write_body(self.body, body, self.encoding)

    @property
    def body(self) -> BytesIO:
        return self._body

    @body.setter
    def body(self, value: Union[str, bytes, bytearray, BytesIO]) -> None:
        if isinstance(value, BytesIO):
            self._body = value
            return

        self._body = BytesIO()
        self.write(value)

    @property
    def writable(self) -> bool:
        return not self._body.closed

    @property
    def headers(self) -> HttpHeaders:
        return self._headers

    def close(self) -> None:
        self._body.close()

    def __str__(self) -> str:
        self._body.seek(0)
        return self._body.read().decode(self.encoding)

    def __eq__(self, other) -> bool:
        if not isinstance(other, HttpResponse):
            return False

        return (
            self.headers == other.headers
            and self.status_code == other.status_code
            and self.encoding == other.encoding
            and self.body.getbuffer().nbytes == other.body.getbuffer().nbytes
        )


__all__ = ["HttpResponse"]
