import glob
import importlib
from os import path, getcwd
from typing import Callable, List, Optional, Union

from .errors import ApplicationError
from .http.http_error import NotFoundError
from .http.http_method import HttpMethod
from .http.http_request import HttpRequest
from .http.http_response import HttpResponse
from .middleware.application_middleware import ApplicationMiddleware
from .middleware.middleware import Middleware, MiddlewarePipeline
from .routing import Route, Router
from .serverless.wrapper import create_serverless_function


class _Loader:
    _loaded_modules: List[str] = []

    @classmethod
    def load(cls, ns: str) -> List[str]:
        # Take the first ns part to understand related system path
        ns_parts = ns.split(".")
        base_module = importlib.import_module(ns_parts[0])
        module_paths = getattr(base_module, "__path__", [getcwd()])
        base_path = module_paths[0]

        # Create glob expression to look up for relevant python files
        glob_path = path.join(base_path, path.sep.join(ns_parts[1:])) + ".py"
        file_list = glob.glob(glob_path)

        # Convert file name list back to module list
        module_list = [ns_parts[0] + file[len(base_path) : -3].replace(path.sep, ".") for file in file_list]

        return [module_name for module_name in module_list if cls._load(module_name)]

    @classmethod
    def _load(cls, module) -> bool:
        if module in cls._loaded_modules:
            return True
        loaded = True
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            loaded = False

        cls._loaded_modules.append(module)
        return loaded


class Application:
    def __init__(self, *middleware: Union[Middleware, Callable]):
        self.parent: Optional[Application] = None
        self._middleware = MiddlewarePipeline()
        for item in middleware:
            self._middleware.append(item)

        self.namespace = ["/"]
        self.router = Router()
        self._loaded_modules: List[str] = []
        self._cached_middleware: Optional[MiddlewarePipeline] = None

    def _append_route(
        self,
        method: HttpMethod,
        route: Route,
        handler: Callable[[HttpRequest], HttpResponse],
    ):
        if self.parent:
            self.parent._append_route(method, route, handler)

        self.router.append(route, handler, method)

    def _create_route(self, route: str, attributes: dict) -> Route:
        base_uri = "".join(self.namespace[1:])
        return Route(base_uri + route, attributes)

    def get(self, route: str, **attributes) -> Callable:
        def _get(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.GET, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _get

    def post(self, route: str, **attributes) -> Callable:
        def _post(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.POST, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _post

    def put(self, route: str, **attributes) -> Callable:
        def _put(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.PUT, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _put

    def patch(self, route: str, **attributes) -> Callable:
        def _patch(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.PATCH, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _patch

    def delete(self, route: str, **attributes) -> Callable:
        def _delete(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.DELETE, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _delete

    def head(self, route: str, **attributes) -> Callable:
        def _head(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.HEAD, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _head

    def options(self, route: str, **attributes) -> Callable:
        def _options(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.OPTIONS, r, handler)
            return create_serverless_function(handler, r, self._middleware)

        return _options

    def any(self, route: str, **attributes) -> Callable:
        def _any(handler: Callable) -> Callable:
            r = self._create_route(route, attributes)
            self._append_route(HttpMethod.GET, r, handler)
            self._append_route(HttpMethod.POST, r, handler)
            self._append_route(HttpMethod.PUT, r, handler)
            self._append_route(HttpMethod.PATCH, r, handler)
            self._append_route(HttpMethod.DELETE, r, handler)
            self._append_route(HttpMethod.HEAD, r, handler)
            self._append_route(HttpMethod.OPTIONS, r, handler)

            return create_serverless_function(handler, r, self._middleware)

        return _any

    def group(self, base_route: str) -> "Application":
        self.namespace.append(base_route)
        return self

    def __enter__(self) -> "Application":
        child_app = Application()
        child_app._middleware = self._middleware
        child_app.namespace = self.namespace
        child_app.parent = self
        child_app._loaded_modules = self._loaded_modules

        return child_app

    def __exit__(self, *args) -> "Application":
        self.namespace.pop()
        return self

    def __call__(self, request: HttpRequest) -> HttpResponse:
        try:
            route, handler = self.router.match(request.path, request.method)
            request.path_parameters = route.parameters
            request.route = route
            request.attributes["__handler__"] = handler
        except NotFoundError:

            def _handler(req: HttpRequest) -> HttpResponse:
                raise NotFoundError()

            request.attributes["__handler__"] = _handler

        return self._application_middleware(request)

    def use(self, namespace: str) -> None:
        try:
            self._loaded_modules = self._loaded_modules + _Loader.load(namespace)
        except ModuleNotFoundError as e:
            raise ApplicationError.for_invalid_namespace(namespace) from e

    @property
    def _application_middleware(self) -> MiddlewarePipeline:
        if self._cached_middleware is None:
            middleware = MiddlewarePipeline(self._middleware.queue)
            middleware.append(ApplicationMiddleware(self.router))
            self._cached_middleware = middleware

        return self._cached_middleware


__all__ = ["Application"]
