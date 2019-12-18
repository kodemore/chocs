from abc import ABC
from abc import abstractmethod

from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse


class MiddlewareHandler(ABC):
    @abstractmethod
    def __call__(self, request: HttpRequest) -> HttpResponse:
        pass


__all__ = ["MiddlewareHandler"]
