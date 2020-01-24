from typing import Any
from typing import Callable
from typing import Dict
from typing import Union

from .http_method import HttpMethod
from .http_request import HttpRequest
from .middleware import Middleware
from .middleware import MiddlewarePipeline
from .middleware import RoutingMiddleware
from .routing.route import Route


class Application:
    def __init__(self, *middleware: Union[Middleware, Callable]):
        self.middleware = MiddlewarePipeline()
        for item in middleware:
            self.middleware.append(item)

    def __call__(self, env: Dict[str, Any], start: Callable) -> Any:
        request = HttpRequest.from_wsgi(env)
        response = self.middleware(request)

        start(
            str(response.status_code),
            [(key, value) for key, value in response.headers.items()],
        )
        response.body.seek(0)
        return response.body


class ApplicationRouter(RoutingMiddleware):
    def get(self, route: str, **patterns) -> Callable:
        def _get(handler: Callable) -> Callable:
            self.methods[HttpMethod.GET].append(Route(route, **patterns), handler)
            return handler

        return _get

    def post(self, route: str, **patterns) -> Callable:
        def _post(handler: Callable) -> Callable:
            self.methods[HttpMethod.POST].append(Route(route, **patterns), handler)
            return handler

        return _post

    def put(self, route: str, **patterns) -> Callable:
        def _put(handler: Callable) -> Callable:
            self.methods[HttpMethod.PUT].append(Route(route, **patterns), handler)
            return handler

        return _put

    def patch(self, route: str, **patterns) -> Callable:
        def _patch(handler: Callable) -> Callable:
            self.methods[HttpMethod.PATCH].append(Route(route, **patterns), handler)
            return handler

        return _patch

    def delete(self, route: str, **patterns) -> Callable:
        def _delete(handler: Callable) -> Callable:
            self.methods[HttpMethod.DELETE].append(Route(route, **patterns), handler)
            return handler

        return _delete

    def head(self, route: str, **patterns) -> Callable:
        def _head(handler: Callable) -> Callable:
            self.methods[HttpMethod.HEAD].append(Route(route, **patterns), handler)
            return handler

        return _head

    def options(self, route: str, **patterns) -> Callable:
        def _options(handler: Callable) -> Callable:
            self.methods[HttpMethod.OPTIONS].append(Route(route, **patterns), handler)
            return handler

        return _options


router = ApplicationRouter()


def serve(*middleware, host: str = "0.0.0.0", port: int = 80) -> None:
    if not middleware:
        application = Application(router)
    else:
        application = Application(*middleware)

    try:
        from bjoern import run

        run(application, host=host, port=port)
    except ImportError as error:
        raise RuntimeError(
            "`bjoern` module could not be found, please run `pip install bjoern`."
        )


__all__ = ["Application", "router", "serve"]
