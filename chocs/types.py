from typing import Callable

from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse

HttpHandlerFunction = Callable[[HttpRequest], HttpResponse]


__all__ = ["HttpHandlerFunction"]
