import base64
import logging
import os
from io import BytesIO
from typing import Callable, Any, Dict

from .http_headers import HttpHeaders
from .http_query_string import HttpQueryString
from .http_request import HttpRequest
from .http_response import HttpResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


IS_SERVERLESS_ENVIRONMENT = bool(
    os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or
    os.environ.get("LAMBDA_RUNTIME_DIR") or
    os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
)


def create_http_request_from_serverless(event: Dict[str, Any], context: Dict[str, Any]) -> HttpRequest:
    body = get_normalised_body_from_serverless(event)
    request_context = event.get("requestContext", {})
    http_context = request_context.get("http", {})

    headers = event["headers"]
    headers["Cookie"] = "; ".join(event.get("cookies", []))
    headers["Content-Length"] = str(body.getbuffer().nbytes)

    # Set serverless related additional headers
    if request_context.get("requestId"):
        headers["x-serverless-request-id"] = request_context.get("requestId")
    if request_context.get("stage"):
        headers["x-serverless-stage"] = request_context.get("stage")
    if headers.get("x-amzn-trace-id"):
        headers["x-serverless-trace-id"] = headers["x-amzn-trace-id"]

    request = HttpRequest(
        method=http_context["method"],
        path=http_context["path"],
        body=body,
        query_string=HttpQueryString(event.get("rawQueryString", "")),
        headers=HttpHeaders(headers)
    )
    request.path_parameters = event.get("pathParameters", {})

    request.aws_context = context
    request.aws_event = event

    return request


def get_normalised_body_from_serverless(event: Dict[str, Any]) -> BytesIO:
    body = event.get("body", "")
    if event.get("isBase64Encoded", False):
        body = base64.b64decode(body)

    if isinstance(body, str):
        body = body.encode("utf-8")

    return BytesIO(body)


def make_serverless_callback(func: Callable[[HttpRequest], HttpResponse]) -> Callable:
    def _handle_serverless_request(event: Dict[str, Any], context: Dict[str, Any]) -> dict:
        request = create_http_request_from_serverless(event, context)
        response = func(request)

        normalised_headers = {}
        for key, value in response.headers.items():
            normalised_headers[key] = value

        response.body.seek(0)
        body = response.body.read()
        logger.info("Sending Response")
        logger.info("status code")
        logger.info(response.status_code)
        logger.info(normalised_headers)
        logger.info(base64.b64encode(body))



        return {
            "isBase64Encoded": True,
            "statusCode": response.status_code,
            "headers": normalised_headers,
            "body": base64.b64encode(body),
        }

    return _handle_serverless_request
