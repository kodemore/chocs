from dataclasses import dataclass

import json
import pytest
from os import path

from chocs import Application, HttpMethod, HttpRequest, HttpResponse
from chocs.json_schema.errors import PropertyValueError, RequiredPropertyError
from chocs.middleware import OpenApiMiddleware
from chocs.middleware.open_api_middleware import QueryValidationError, PathValidationError, HeadersValidationError, CookiesValidationError


def test_pass_valid_request_with_body() -> None:
    app = _mockup_app()
    _add_create_pet_route(app)
    body = json.dumps({"name": "Bob", "tag": "test-tag",})
    app(
        HttpRequest(
            HttpMethod.POST,
            "/pets",
            body=body,
            headers={"content-type": "application/json"},
        )
    )


def test_fail_request_with_missing_property() -> None:
    app = _mockup_app()
    _add_create_pet_route(app)
    body = json.dumps({"tag": "test-tag",})

    with pytest.raises(RequiredPropertyError):
        app(
            HttpRequest(
                HttpMethod.POST,
                "/pets",
                body=body,
                headers={"content-type": "application/json"},
            )
        )


def test_fail_request_with_invalid_value() -> None:
    app = _mockup_app()
    _add_create_pet_route(app)
    body = json.dumps({"name": 11,})

    with pytest.raises(PropertyValueError) as e:
        app(
            HttpRequest(
                HttpMethod.POST,
                "/pets",
                body=body,
                headers={"content-type": "application/json"},
            )
        )

    assert str(e.value) == (
        "Property `name` failed to pass validation: "
        "Passed value must be valid <class 'str'> type. "
        "Actual type passed was <class 'int'>."
    )


def test_pass_valid_request_with_query() -> None:
    app = _mockup_app()

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    app(HttpRequest(HttpMethod.GET, "/pets", query_string="tags=bla&tags=bla2"))


def test_fail_request_with_query_invalid_type() -> None:
    app = _mockup_app()

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    with pytest.raises(QueryValidationError):
        app(HttpRequest(HttpMethod.GET, "/pets", query_string="tags=1"))


def test_fail_request_with_query_missing_field() -> None:
    app = _mockup_app()

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    with pytest.raises(QueryValidationError):
        app(HttpRequest(HttpMethod.GET, "/pets"))


def test_turn_off_query_validation() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    app = Application(OpenApiMiddleware(openapi_file, validate_query=False))

    @app.get("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    assert app(HttpRequest(HttpMethod.GET, "/pets"))


def test_body_validation_handles_arrays() -> None:
    openapi_file = path.realpath(
        path.dirname(__file__) + "/../fixtures/openapi_request_body_array.yml"
    )
    app = Application(
        OpenApiMiddleware(openapi_file, validate_body=True, validate_query=True)
    )

    @app.post("/pets")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    request = HttpRequest(
        HttpMethod.POST,
        "/pets",
        body=json.dumps(
            [{"name": "Name1", "tag": "Tag1",}, {"name": "Name2", "tag": "Tag2",},]
        ),
        headers={"content-type": "application/json"},
    )
    assert app(request=request)


def test_pass_valid_request_with_path() -> None:
    # given
    app = _mockup_app()

    @app.get("/pets/{id}")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    # when
    result = app(HttpRequest(HttpMethod.GET, "/pets/12"))

    # then
    assert result


def test_fail_invalid_request_with_path() -> None:
    # given
    app = _mockup_app()

    @app.get("/pets/{id}")
    def get_pets(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")

    # when
    with pytest.raises(PathValidationError) as error:
        result = app(HttpRequest(HttpMethod.GET, "/pets/apet"))

    # then
    assert error.value.error.message == PropertyValueError.message


def _mockup_app() -> Application:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    app = Application(OpenApiMiddleware(openapi_file))

    return app


def _add_create_pet_route(app: Application) -> None:
    @app.post("/pets")
    def create_pet(request: HttpRequest) -> HttpResponse:
        return HttpResponse("OK")
