from typing import Callable

from .http_request import HttpRequest
from .http_response import HttpResponse

HttpHandlerFunction = Callable[[HttpRequest], HttpResponse]


__all__ = ["HttpHandlerFunction"]
