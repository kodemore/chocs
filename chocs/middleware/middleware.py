from abc import ABC, abstractmethod
from typing import Callable, Union, List

from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse


class MiddlewareHandler(ABC):
    @abstractmethod
    def __call__(self, request: HttpRequest) -> HttpResponse:
        ...


class Middleware(ABC):
    @abstractmethod
    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        ...


MiddlewareFunction = Callable[[HttpRequest, MiddlewareHandler], HttpResponse]


class MiddlewareCursor(MiddlewareHandler):
    def __init__(self, queue: List, parent: MiddlewareHandler):
        self.queue: List[Middleware] = [item for item in queue]
        self.parent = parent

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self.queue:
            return self.parent(request)

        middleware: Union[Middleware, MiddlewareFunction] = self.queue.pop(0)
        next = MiddlewareCursor(self.queue, self)

        if isinstance(middleware, Middleware):
            return middleware.handle(request, next)
        return middleware(request, next)


class EmptyPipelineHandler(MiddlewareHandler):
    def __call__(self, request: HttpRequest) -> HttpResponse:
        raise RuntimeError("Middleware pipe is empty.")


class MiddlewarePipeline(MiddlewareHandler, Middleware):
    def __init__(self, queue: List = []):
        self.queue: List = []
        if queue:
            self.queue = [item for item in queue]

    def append(self, *middleware: Union[Middleware, Callable]) -> None:
        for item in middleware:
            self.queue.append(item)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.handle(request, EmptyPipelineHandler())

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        return (MiddlewareCursor(self.queue, next)).__call__(request)

    @property
    def empty(self) -> bool:
        return len(self.queue) <= 0


__all__ = [
    "MiddlewareHandler",
    "Middleware",
    "MiddlewareFunction",
    "MiddlewareCursor",
    "MiddlewarePipeline",
]
