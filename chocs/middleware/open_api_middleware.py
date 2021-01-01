import inspect
from typing import Callable, Dict

from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.json_schema.json_schema import OpenApiSchema
from chocs.json_schema.schema_validator import build_validator_from_schema
from chocs.middleware import Middleware, MiddlewareHandler


class OpenApiMiddleware(Middleware):
    def __init__(self, openapi_filename: str):
        self.openapi = OpenApiSchema(openapi_filename)
        self.validators: Dict[str, Callable] = {}

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        route = request.route
        if not route:
            return next(request)

        if route.route not in self.validators:
            path = route.route.replace("/", "\\/")
            method = str(request.method).lower()
            try:
                body_schema = self.openapi.query(
                    f"/paths/{path}/{method}/requestBody/content/application\\/json/schema"
                )
                self.validators[route.route] = build_validator_from_schema(body_schema)
            except KeyError:
                self.validators[route.route] = lambda obj: obj

        body_validator = self.validators[route.route]
        try:
            parsed_body = dict(request.parsed_body)  # type: ignore
        except Exception:
            parsed_body = {}
        valid_body = body_validator(parsed_body)

        if "parsed_body" in route.attributes and inspect.isclass(route.attributes["parsed_body"]):
            constructor = route.attributes["parsed_body"]
            request._parsed_body = constructor(**valid_body)

        return next(request)


__all__ = ["OpenApiMiddleware"]
