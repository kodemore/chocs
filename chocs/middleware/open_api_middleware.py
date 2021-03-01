from typing import Any, Callable, Dict, List, Optional, Union, TypeVar

from chocs.http_message import JsonHttpMessage
from chocs.http_method import HttpMethod
from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.json_schema.errors import InvalidInputValidationError, ValidationError
from chocs.json_schema.json_schema import JsonReference, OpenApiSchema
from chocs.json_schema.schema_validator import build_validator_from_schema
from chocs.middleware import Middleware, MiddlewareHandler
from chocs.routing import Route

_UNDEFINED = object()


class OpenApiValidationError(ValueError):
    pass


class PathValidationError(OpenApiValidationError):
    def __init__(self, validation_error: ValidationError):
        self.error = validation_error


class QueryValidationError(OpenApiValidationError):
    def __init__(self, validation_error: ValidationError):
        self.error = validation_error


class CookiesValidationError(OpenApiValidationError):
    def __init__(self, validation_error: ValidationError):
        self.error = validation_error


class BodyValidationError(OpenApiValidationError):
    def __init__(self, validation_error: ValidationError):
        self.error = validation_error


class HeadersValidationError(OpenApiValidationError):
    def __init__(self, validation_error: ValidationError):
        self.error = validation_error


class _OpenApiValidatorGroup:
    def __init__(
        self,
        validate_body: bool = True,
        validate_headers: bool = True,
        validate_query: bool = True,
        validate_path: bool = True,
        validate_cookies: bool = True,
    ):
        self.validate_body = validate_body
        self.validate_headers = validate_headers
        self.validate_query = validate_query
        self.validate_path = validate_path
        self.validate_cookies = validate_cookies

        self._query_schema: Union[Dict[str, Any], Any] = _UNDEFINED
        self._body_schema: Union[Dict[str, Any], Any] = _UNDEFINED
        self._header_schema: Union[Dict[str, Any], Any] = _UNDEFINED
        self._path_schema: Union[Dict[str, Any], Any] = _UNDEFINED
        self._cookie_schema: Union[Dict[str, Any], Any] = _UNDEFINED

        self._query_validator: Union[Callable, Any] = _UNDEFINED
        self._body_validator: Union[Callable, Any] = _UNDEFINED
        self._path_validator: Union[Callable, Any] = _UNDEFINED
        self._cookie_validator: Union[Callable, Any] = _UNDEFINED
        self._header_validator: Union[Callable, Any] = _UNDEFINED

    def _get_schema_for(self, attribute: str) -> Dict[str, Any]:
        full_attribute_name = "_" + attribute + "_schema"
        if getattr(self, full_attribute_name) is _UNDEFINED:
            setattr(
                self,
                full_attribute_name,
                {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            )

        return getattr(self, full_attribute_name)

    def _get_validator_for(self, attribute: str) -> Callable:
        attribute_validator_name = "_" + attribute + "_validator"
        attribute_schema_name = "_" + attribute + "_schema"
        if getattr(self, attribute_validator_name) is _UNDEFINED:
            if getattr(self, attribute_schema_name) is not _UNDEFINED:
                setattr(
                    self, attribute_validator_name, build_validator_from_schema(getattr(self, attribute_schema_name))
                )
            else:
                setattr(self, attribute_validator_name, lambda x: x)

        return getattr(self, attribute_validator_name)

    @property
    def query_validator(self) -> Callable:
        return self._get_validator_for("query")

    @property
    def query_schema(self) -> Dict[str, Any]:
        return self._get_schema_for("query")

    @property
    def header_validator(self) -> Callable:
        return self._get_validator_for("header")

    @property
    def header_schema(self) -> Dict[str, Any]:
        return self._get_schema_for("header")

    @property
    def cookie_validator(self) -> Callable:
        return self._get_validator_for("cookie")

    @property
    def cookie_schema(self) -> Dict[str, Any]:
        return self._get_schema_for("cookie")

    @property
    def path_validator(self) -> Callable:
        return self._get_validator_for("path")

    @property
    def path_schema(self) -> Dict[str, Any]:
        return self._get_schema_for("path")

    @property
    def body_validator(self) -> Callable:
        return self._get_validator_for("body")

    @property
    def body_schema(self) -> Dict[str, Any]:
        return self._get_schema_for("body")

    def validate(self, request: HttpRequest) -> None:
        if self.validate_body and self._body_schema is not _UNDEFINED:
            self._validate_body(request)
        if self.validate_path and self._path_schema is not _UNDEFINED:
            self._validate_path(request)
        if self.validate_headers and self._header_schema is not _UNDEFINED:
            self._validate_headers(request)
        if self.validate_query and self._query_schema is not _UNDEFINED:
            self._validate_query(request)
        if self.validate_cookies and self._cookie_schema is not _UNDEFINED:
            self._validate_cookies(request)

    def _validate_body(self, request: HttpRequest) -> None:
        parsed_body: Union[Dict, List]

        if not hasattr(request.parsed_body, "data"):
            raise InvalidInputValidationError(message="Request body could not be validated.")

        if isinstance(request.parsed_body.data, dict) or isinstance(request.parsed_body.data, list):  # type: ignore
            parsed_body = request.parsed_body.data  # type: ignore
        else:
            raise InvalidInputValidationError(message="Request body could not be validated.")

        request._parsed_body = self.body_validator(parsed_body)

    def _validate_path(self, request: HttpRequest) -> None:
        path_parameters = request.path_parameters
        try:
            self.path_validator(path_parameters)
        except ValidationError as error:
            raise PathValidationError(error) from error

    def _validate_headers(self, request: HttpRequest) -> None:
        # We have to normalise headers before validation
        headers = {}
        for name, values in request.headers.items():
            headers[name] = values[0] if len(values) == 1 else values

        try:
            self.header_validator(headers)
        except ValidationError as error:
            raise HeadersValidationError(error) from error

    def _validate_query(self, request: HttpRequest) -> None:
        query = dict(request.query_string)
        try:
            self.query_validator(query)
        except ValidationError as error:
            raise QueryValidationError(error) from error

    def _validate_cookies(self, request: HttpRequest) -> None:
        # We have to normalise cookies before validation
        cookies = {}
        for name, cookie in request.cookies.items():
            cookies[name] = str(cookie)

        try:
            self.cookie_validator(cookies)
        except ValidationError as error:
            raise CookiesValidationError(error) from error


class OpenApiMiddleware(Middleware):
    def __init__(
        self,
        openapi_filename: str,
        validate_body: bool = True,
        validate_headers: bool = True,
        validate_query: bool = True,
        validate_path: bool = True,
        validate_cookies: bool = True,
    ):
        self.openapi = OpenApiSchema(openapi_filename)

        self.validate_body = validate_body
        self.validate_headers = validate_headers
        self.validate_query = validate_query
        self.validate_path = validate_path
        self.validate_cookies = validate_cookies

        self._validators: Dict[str, _OpenApiValidatorGroup] = {}

    def handle(self, request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
        route = request.route
        if not route:
            return next(request)

        validator_cache_key = f"{request.method} {route.route}".lower()

        if validator_cache_key not in self._validators:
            self._validators[validator_cache_key] = self._generate_validator_group_for(
                route.route, request.method, str(request.headers.get("content-type", "application/json"))
            )

        self._validators[validator_cache_key].validate(request)
        return next(request)

    def _generate_validator_group_for(
        self, route: str, method: HttpMethod, content_type: str
    ) -> _OpenApiValidatorGroup:
        path = route.replace("/", "\\/")
        method_name = str(method).lower()

        validator_group = _OpenApiValidatorGroup(
            self.validate_body, self.validate_headers, self.validate_query, self.validate_path, self.validate_cookies
        )

        try:
            open_api_path_fragment = self.openapi.query(f"/paths/{path}")
            open_api_fragment = open_api_path_fragment[method_name]
        except KeyError:
            return validator_group

        if self.validate_body:
            if (
                "requestBody" in open_api_fragment
                and "content" in open_api_fragment["requestBody"]
                and content_type in open_api_fragment["requestBody"]["content"]
                and "schema" in open_api_fragment["requestBody"]["content"][content_type]
            ):
                validator_group._body_schema = open_api_fragment["requestBody"]["content"][content_type]["schema"]
            else:
                validator_group.validate_body = False

        validate_parameters = False
        if "parameters" in open_api_path_fragment:
            for parameter in open_api_path_fragment["parameters"]:
                self._process_path_parameter(parameter, validator_group)
            validate_parameters = True

        if "parameters" in open_api_fragment:
            for parameter in open_api_fragment["parameters"]:
                self._process_path_parameter(parameter, validator_group)
            validate_parameters = True

        if not validate_parameters:
            validator_group.validate_cookies = False
            validator_group.validate_path = False
            validator_group.validate_query = False
            validator_group.validate_headers = False

        return validator_group

    @staticmethod
    def _process_path_parameter(parameter: dict, validator_group: _OpenApiValidatorGroup) -> None:
        attribute_name = parameter["in"] + "_schema"
        schema = getattr(validator_group, attribute_name)
        if "required" in parameter and parameter["required"]:
            schema["required"].append(parameter["name"])
        if "schema" in parameter:
            schema["properties"][parameter["name"]] = parameter["schema"]


__all__ = ["OpenApiMiddleware"]
