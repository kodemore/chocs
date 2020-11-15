import base64
import logging
import os
from io import BytesIO
from typing import Any
from typing import Callable
from typing import Dict
from urllib.parse import quote_plus

from .http_headers import HttpHeaders
from .http_query_string import HttpQueryString
from .http_request import HttpRequest
from .http_response import HttpResponse
from .routing import Route
from .http_status import HttpStatus


logger = logging.getLogger()
logger.setLevel(logging.INFO)


IS_SERVERLESS_ENVIRONMENT = bool(
    os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or
    os.environ.get("LAMBDA_RUNTIME_DIR") or
    os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
)

TEXT_MIME_TYPES = [
    "application/json",
    "application/javascript",
    "application/xml",
    "application/vnd.api+json",
    "image/svg+xml",
]


def is_http_api_lambda(event: Dict[str, Any]) -> bool:
    if event.get("version") and event["version"] == "2.0":
        return True

    return False


def create_http_request_from_serverless_event(event: Dict[str, Any], context: Dict[str, Any]) -> HttpRequest:
    is_http_api = is_http_api_lambda(event)

    if is_http_api:
        request = create_http_request_from_serverless_http_api(event, context)
    else:
        request = create_http_request_from_serverless_rest_api(event, context)

    return request


def create_http_request_from_serverless_http_api(event: Dict[str, Any], context: Dict[str, Any]) -> HttpRequest:
    body = get_normalised_body_from_serverless(event)
    request_context = event.get("requestContext", {})
    http_context = request_context.get("http", {})

    headers = get_normalised_headers_from_serverless(event)
    headers["Cookie"] = "; ".join(event.get("cookies", []))
    headers["Content-Length"] = str(body.getbuffer().nbytes)

    request = HttpRequest(
        method=http_context["method"],
        path=http_context["path"],
        body=body,
        query_string=HttpQueryString(event.get("rawQueryString", "")),
        headers=HttpHeaders(headers)
    )
    request.path_parameters = event.get("pathParameters", {})

    request.attributes["aws_context"] = context
    request.attributes["aws_event"] = event

    return request


def create_http_request_from_serverless_rest_api(event: Dict[str, Any], context: Dict[str, Any]) -> HttpRequest:
    body = get_normalised_body_from_serverless(event)

    headers = get_normalised_headers_from_serverless(event)
    headers["Content-Length"] = str(body.getbuffer().nbytes)

    raw_query_string = ""
    if event.get("multiValueQueryStringParameters"):
        for key, values in event.get("multiValueQueryStringParameters").items():
            for value in values:
                raw_query_string += f"&{key}={quote_plus(value)}"

        raw_query_string = raw_query_string[1:]

    request = HttpRequest(
        method=event.get("httpMethod", "GET"),
        path=event.get("path", "/"),
        body=body,
        query_string=HttpQueryString(raw_query_string),
        headers=HttpHeaders(headers)
    )
    request.path_parameters = event.get("pathParameters", {})

    request.attributes["aws_context"] = context
    request.attributes["aws_event"] = event

    return request


def get_normalised_headers_from_serverless(event: Dict[str, Any]) -> Dict[str, str]:
    headers = event["headers"]
    request_context = event.get("requestContext", {})  # Set serverless related additional headers
    if request_context.get("requestId"):
        headers["x-serverless-request-id"] = request_context.get("requestId")
    if request_context.get("stage"):
        headers["x-serverless-stage"] = request_context.get("stage")
    if headers.get("x-amzn-trace-id"):
        headers["x-serverless-trace-id"] = headers["x-amzn-trace-id"]

    return headers


def get_normalised_body_from_serverless(event: Dict[str, Any]) -> BytesIO:
    body = event.get("body", "")
    if event.get("isBase64Encoded", False):
        body = base64.b64decode(body)

    if isinstance(body, str):
        body = body.encode("utf-8")

    return BytesIO(body)


def make_serverless_callback(func: Callable[[HttpRequest], HttpResponse], route: Route) -> Callable:
    def _handle_serverless_request(event: Dict[str, Any], context: Dict[str, Any]) -> dict:

        if event.get("source") in ["aws.events", "serverless-plugin-warmup"]:  # lambda warmup should be ignored
            return {
                "statusCode": int(HttpStatus.CONTINUE),
            }

        request = create_http_request_from_serverless_event(event, context)

        route._parameters = request.path_parameters
        request.route = route

        response = func(request)

        return make_serverless_response(event, response)

    return _handle_serverless_request


def make_serverless_response(event: Dict[str, Any], response: HttpResponse) -> Dict[str, Any]:
    logger.info("generating response")
    logger.info(event)
    serverless_response = {"statusCode": int(response.status_code)}

    if "multiValueHeaders" in event:
        serverless_response["multiValueHeaders"] = response.headers._headers
    else:
        serverless_response["headers"] = {key: value for key, value in response.headers.items()}

    # If the request comes from ALB we need to add a status description
    is_elb = event.get("requestContext", {}).get("elb")
    if is_elb:
        logger.info("elb endpoint")
        serverless_response["statusDescription"] = str(response.status_code)

    mimetype = response.headers.get("content-type", "text/plain")

    # If there is no body or empty body we simply dont care about the rest
    body = str(response)
    if not body:
        logger.info("no body")

    if (mimetype.startswith("text/") or mimetype in TEXT_MIME_TYPES) and \
            not response.headers.get("Content-Encoding", ""):

        serverless_response["body"] = body
        serverless_response["isBase64Encoded"] = False
    else:
        serverless_response["body"] = base64.b64encode(body.encode("utf8"))
        serverless_response["isBase64Encoded"] = True

    logger.info(serverless_response)

    return serverless_response
