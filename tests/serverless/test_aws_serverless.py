import json
import os
import pytest
from typing import Callable

from chocs import HttpCookie, HttpQueryString, HttpRequest, HttpResponse, Route
from chocs.middleware import MiddlewarePipeline
from chocs.serverless import AwsServerlessFunction, create_http_request_from_aws_event


@pytest.mark.parametrize(
    "event_file",
    ["fixtures/lambda_http_api_event.json", "fixtures/lambda_rest_api_event.json"],
)
def test_create_http_request_from_serverless_event(event_file: str) -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(open(os.path.join(dir_path, '..', event_file)))

    request = create_http_request_from_aws_event(event_json, {})
    assert isinstance(request, HttpRequest)
    assert request.path == "/test/123"
    assert request.headers.get("accept-encoding", "") == "gzip, deflate, br"
    assert request.headers.get("non-existing", "") == ""
    assert isinstance(request.cookies["Cookie_1"], HttpCookie)
    assert str(request.cookies["Cookie_1"]) == "value"
    assert isinstance(request.query_string, HttpQueryString)
    assert "param_1" in request.query_string
    assert "param_2" in request.query_string
    assert request.query_string.get("param_1") == "value1"
    assert request.query_string.get("param_2") == "value2"


def test_create_http_request_from_serverless_event_without_headers() -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(
        open(
            os.path.join(
                dir_path, "../fixtures/lambda_rest_api_event_without_headers.json"
            )
        )
    )
    request = create_http_request_from_aws_event(event_json, {})
    assert isinstance(request, HttpRequest)
    assert request.headers


def test_create_http_request_from_serverless_event_multipart_image() -> None:
    dir_path = os.path.dirname(os.path.realpath(__file__))

    event_json = json.load(
        open(
            os.path.join(
                dir_path, "../fixtures/lambda_rest_api_multipart_form_image_upload.json"
            )
        )
    )
    request = create_http_request_from_aws_event(event_json, {})
    assert isinstance(request, HttpRequest)
    assert "image" in request.parsed_body


def test_make_serverless_callback() -> None:
    def test_callaback(request: HttpRequest) -> HttpResponse:
        return HttpResponse(request.path)

    serverless_callback = AwsServerlessFunction(test_callaback)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(
        open(os.path.join(dir_path, "../fixtures/lambda_http_api_event.json"))
    )

    response = serverless_callback(event_json, {})

    assert "statusCode" in response
    assert response["statusCode"] == 200
    assert "headers" in response
    assert "body" in response
    assert response["body"] == "/test/123"


def test_middleware_for_serverless() -> None:
    def cors_middleware(
        request: HttpRequest, next: Callable[[HttpRequest], HttpResponse]
    ) -> HttpResponse:
        response = next(request)
        response._headers.set("Access-Control-Allow-Origin", "*")

        return response

    def ok_handler(request: HttpRequest) -> HttpResponse:
        return HttpResponse(status=200)

    middleware_pipeline = MiddlewarePipeline()
    middleware_pipeline.append(cors_middleware)
    serverless_callback = AwsServerlessFunction(
        ok_handler, Route("/"), middleware_pipeline
    )
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(
        open(os.path.join(dir_path, "../fixtures/lambda_http_api_event.json"))
    )

    response = serverless_callback(event_json, {})

    assert "headers" in response
    assert "access-control-allow-origin" in response["headers"]


@pytest.mark.parametrize(
    "content_type",
    [
        "application/json; charset=utf-8",
        "application/x-yaml",
        "text/vnd.yaml",
        "text/yaml",
        "text/x-yaml",
    ],
)
def test_content_types_are_not_base64_encoded(content_type) -> None:
    def test_callback(request: HttpRequest) -> HttpResponse:
        return HttpResponse(
            request.path,
            headers={
                "Content-Type": content_type,
            },
        )

    serverless_callback = AwsServerlessFunction(test_callback)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(
        open(os.path.join(dir_path, "../fixtures/lambda_http_api_event.json"))
    )

    response = serverless_callback(event_json, {})

    assert response["isBase64Encoded"] is False
    assert response["body"] == "/test/123"


@pytest.mark.parametrize("aws_event", [
    "fixtures/lambda_http_api_event.json",
    "fixtures/lambda_rest_api_event.json",
])
def test_can_pass_none_in_path_parameters(aws_event: str) -> None:
    # given
    def test_callback(request: HttpRequest) -> HttpResponse:
        assert request.path_parameters == {}
        return HttpResponse("OK")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    event_json = json.load(
        open(os.path.join(dir_path, "..", aws_event))
    )
    event_json["pathParameters"] = None
    serverless_callback = AwsServerlessFunction(test_callback)

    # when
    response = serverless_callback(event_json, {})

    # then
    assert response["statusCode"] == 200



