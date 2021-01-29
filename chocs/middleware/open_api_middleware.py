import inspect
from typing import Callable, Dict, Any, List, Optional, Union

from chocs.http_method import HttpMethod
from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.json_schema.json_schema import JsonReference, OpenApiSchema
from chocs.json_schema.schema_validator import build_validator_from_schema
from chocs.json_schema.errors import InvalidInputValidationError
from chocs.middleware import Middleware, MiddlewareHandler
from chocs.routing import Route
from chocs.http_message import JsonHttpMessage


class OpenApiMiddleware(Middleware):
    def __init__(self, openapi_filename: str, validate_body: bool = True, validate_query: bool = True):
        self.openapi = OpenApiSchema(openapi_filename)
        self.validate_body = validate_body
        self.validate_query = validate_query
        self.body_validators: Dict[str, Optional[Callable]] = {}
        self.query_validators: Dict[str, Optional[Callable]] = {}

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        route = request.route
        if not route:
            return next(request)

        if self.validate_body:
            self._validate_request_body(request, route)

        if self.validate_query:
            self._validate_query_string(request, route)

        return next(request)

    def _validate_query_string(self, request: HttpRequest, route: Route) -> None:
        query_validator = self._get_query_validator(route.route, request.method)
        if not query_validator:
            return

        query_validator(dict(request.query_string) if request.query_string else {})

    def _validate_request_body(self, request: HttpRequest, route: Route) -> None:
        body_validator = self._get_body_validator(route.route, request.method)
        if not body_validator:
            return

        if not isinstance(request.parsed_body, JsonHttpMessage):
            raise InvalidInputValidationError(message="Request body is not valid application/json request.")

        parsed_body: Union[Dict, List]

        # we expect here only types provided by json parser, we should ignore everything what is not dict or list.
        if isinstance(request.parsed_body.data, dict) or isinstance(request.parsed_body.data, list):
            parsed_body = request.parsed_body.data
        else:
            raise InvalidInputValidationError(message="Request body could not be validated.")

        valid_body = body_validator(parsed_body)

        if "parsed_body" not in route.attributes:
            return

        if not inspect.isclass(route.attributes["parsed_body"]):
            return

        strict = route.attributes["strict"] if "strict" in route.attributes else True
        constructor = route.attributes["parsed_body"]
        request._parsed_body = None

        if not strict:

            def _get_non_strict_parsed_body() -> Any:

                instance = constructor.__new__(constructor)
                for prop_name, prop_value in valid_body.items():
                    setattr(instance, prop_name, prop_value)

                if hasattr(instance, "__post_init__"):
                    instance.__post_init__()

                return instance

            request._parsed_body_getter = _get_non_strict_parsed_body

            return

        def _get_strict_parsed_body() -> Any:
            return constructor(**valid_body)

        request._parsed_body_getter = _get_strict_parsed_body

    def _get_query_validator(self, route: str, method: HttpMethod) -> Optional[Callable]:
        if route not in self.query_validators:
            path = route.replace("/", "\\/")
            method_name = str(method).lower()
            try:
                query_parameters = [
                    item
                    for item in self.openapi.query(f"/paths/{path}/{method_name}/parameters")
                    if item["in"] == "query"
                ]
                query_schema = {
                    "type": "object",
                    "properties": {},
                    "required": [],
                }
                for param in query_parameters:
                    if isinstance(param, JsonReference):
                        param = param.data
                    param_name = param.get("name", "_")
                    query_schema["properties"][param_name] = param["schema"]  # type:ignore
                    if param["required"]:
                        query_schema["required"].append(param_name)  # type:ignore

                self.query_validators[route] = build_validator_from_schema(query_schema)
            except KeyError:
                self.query_validators[route] = None

        return self.query_validators[route]

    def _get_body_validator(self, route: str, method: HttpMethod) -> Optional[Callable]:
        if route not in self.body_validators:
            path = route.replace("/", "\\/")
            method_name = str(method).lower()
            try:
                body_schema = self.openapi.query(
                    f"/paths/{path}/{method_name}/requestBody/content/application\\/json/schema"
                )
                self.body_validators[route] = build_validator_from_schema(body_schema)
            except KeyError:
                self.body_validators[route] = None

        return self.body_validators[route]


__all__ = ["OpenApiMiddleware"]
