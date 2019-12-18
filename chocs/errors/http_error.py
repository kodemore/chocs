from typing import Optional

from chocs.http_response import HttpResponse


class HttpError(HttpResponse, Exception):
    status_code: int = 500
    http_message = "Internal Server Error"

    def __init__(
        self, http_message: Optional[str] = None, status_code: Optional[int] = None
    ):
        super().__init__(status=status_code if status_code else self.status_code)
        self.write(http_message if http_message else self.http_message)


__all__ = ["HttpError"]
