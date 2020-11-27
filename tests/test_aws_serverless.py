import json
import os
from typing import Callable

import pytest

from chocs import HttpApplication
from chocs import HttpCookie
from chocs import HttpQueryString
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import Route
from chocs.middleware import MiddlewarePipeline
from chocs.serverless import create_http_request_from_serverless_event
from chocs.serverless import make_serverless_callback


@pytest.mark.parametrize("event_file", [
    "fixtures/lambda_http_api_event.json",
    "fixtures/lambda_rest_api_event.json"
])
def test_create_http_request_from_serverless_event(event_file: str) -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(open(os.path.join(dir_path, event_file)))

    request = create_http_request_from_serverless_event(event_json, {})
    assert isinstance(request, HttpRequest)
    assert request.path == "/test/123"
    assert request.headers.get("accept-encoding", "") == "gzip, deflate, br"
    assert request.headers.get("non-existing", "") == ""
    assert isinstance(request.cookies["Cookie_1"], HttpCookie)
    assert str(request.cookies["Cookie_1"]) == "value"
    assert isinstance(request.query_string, HttpQueryString)
    assert 'param_1' in request.query_string
    assert 'param_2' in request.query_string
    assert request.query_string.get("param_1") == "value1"
    assert request.query_string.get("param_2") == "value2"


def test_make_serverless_callback() -> None:
    def test_callaback(request: HttpRequest) -> HttpResponse:
        return HttpResponse(request.path)

    serverless_callback = make_serverless_callback(MiddlewarePipeline(), test_callaback, Route("/test/{id}"))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(open(os.path.join(dir_path, "fixtures/lambda_http_api_event.json")))

    response = serverless_callback(event_json, {})

    assert "statusCode" in response
    assert response["statusCode"] == 200
    assert "headers" in response
    assert "body" in response
    assert response["body"] == "/test/123"


def test_middleware_for_serverless() -> None:

    def cors_middleware(request: HttpRequest, next: Callable[[HttpRequest], HttpResponse]) -> HttpResponse:
        response = next(request)
        response._headers.set("Access-Control-Allow-Origin", "*")

        return response

    app = HttpApplication(cors_middleware)

    def ok_handler(request: HttpRequest) -> HttpResponse:
        return HttpResponse(status=200)

    serverless_callback = make_serverless_callback(app.middleware, ok_handler, Route("/test/{id}"))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(open(os.path.join(dir_path, "fixtures/lambda_http_api_event.json")))

    response = serverless_callback(event_json, {})

    assert "headers" in response
    assert "access-control-allow-origin" in response["headers"]

