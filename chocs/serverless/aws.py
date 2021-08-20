import base64
from cgi import parse_header
from io import BytesIO
from typing import Any, Dict
from urllib.parse import quote_plus

from chocs.http.http_headers import HttpHeaders
from chocs.http.http_query_string import HttpQueryString
from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse
from chocs.http.http_status import HttpStatus
from .serverless import ServerlessFunction

TEXT_MIME_TYPES = [
    "application/json",
    "application/javascript",
    "application/xml",
    "application/x-yaml",
    "application/vnd.api+json",
    "image/svg+xml",
    "text/vnd.yaml",
    "text/yaml",
    "text/x-yaml",
]

AwsEvent = Dict[str, Any]
AwsContext = Dict[str, Any]


class AwsServerlessFunction(ServerlessFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.middleware_enabled = True

    def __call__(self, *args):
        event: AwsEvent = args[0]
        context: AwsContext = args[0]

        if event.get("source") in [
            "aws.events",
            "serverless-plugin-warmup",
        ]:  # lambda warmup should be ignored
            return {
                "statusCode": int(HttpStatus.CONTINUE),
            }
        request = create_http_request_from_aws_event(event, context)
        return format_response_to_aws(event, super().__call__(request))


def is_http_api_lambda(event: AwsEvent) -> bool:
    if event.get("version") and event["version"] == "2.0":
        return True

    return False


def format_response_to_aws(event: AwsEvent, response: HttpResponse) -> Dict[str, Any]:
    serverless_response: Dict[str, Any] = {"statusCode": int(response.status_code)}

    headers = response.headers
    for cookie in response.cookies.values():
        headers.set("Set-Cookie", cookie.serialise())

    if "multiValueHeaders" in event:
        serverless_response["multiValueHeaders"] = headers._headers
    else:
        serverless_response["headers"] = {key: value for key, value in headers.items()}

    # If the request comes from ALB we need to add a status description
    is_elb = event.get("requestContext", {}).get("elb")
    if is_elb:
        serverless_response["statusDescription"] = str(response.status_code)

    content_type_header = response.headers.get("content-type", "text/plain")
    if not isinstance(content_type_header, str):
        content_type_header = content_type_header[0]
    mimetype, content_type_options = parse_header(content_type_header)
    body = str(response)

    if (mimetype.startswith("text/") or mimetype in TEXT_MIME_TYPES) and not response.headers.get(
        "Content-Encoding", ""
    ):
        serverless_response["body"] = body
        serverless_response["isBase64Encoded"] = False
    else:
        serverless_response["body"] = base64.b64encode(body.encode("utf8"))
        serverless_response["isBase64Encoded"] = True

    return serverless_response


def create_http_request_from_aws_event(event: AwsEvent, context: AwsContext) -> HttpRequest:
    is_http_api = is_http_api_lambda(event)

    if is_http_api:
        request = create_http_request_from_aws_http_api(event, context)
    else:
        request = create_http_request_from_aws_rest_api(event, context)

    return request


def create_http_request_from_aws_http_api(event: AwsEvent, context: AwsContext) -> HttpRequest:
    body = get_normalised_body_from_aws(event)
    request_context = event.get("requestContext", {})
    http_context = request_context.get("http", {})

    headers = get_normalised_headers_from_aws(event)
    headers["Cookie"] = "; ".join(event.get("cookies", []))
    headers["Content-Length"] = str(body.getbuffer().nbytes)

    request = HttpRequest(
        method=http_context["method"],
        path=http_context["path"],
        body=body,
        query_string=HttpQueryString(event.get("rawQueryString", "")),
        headers=HttpHeaders(headers),
    )
    request.path_parameters = event.get("pathParameters", {})

    request.attributes["aws_context"] = context
    request.attributes["aws_event"] = event

    return request


def create_http_request_from_aws_rest_api(event: AwsEvent, context: AwsContext) -> HttpRequest:
    body = get_normalised_body_from_aws(event)

    headers = get_normalised_headers_from_aws(event)
    headers["Content-Length"] = str(body.getbuffer().nbytes)

    raw_query_string = ""
    if event.get("multiValueQueryStringParameters"):
        for key, values in event.get("multiValueQueryStringParameters", {}).items():
            for value in values:
                raw_query_string += f"&{key}={quote_plus(value)}"

        raw_query_string = raw_query_string[1:]

    request = HttpRequest(
        method=event.get("httpMethod", "GET"),
        path=event.get("path", "/"),
        body=body,
        query_string=HttpQueryString(raw_query_string),
        headers=HttpHeaders(headers),
    )
    request.path_parameters = event.get("pathParameters", {})

    request.attributes["aws_context"] = context
    request.attributes["aws_event"] = event

    return request


def get_normalised_headers_from_aws(event: AwsEvent) -> Dict[str, str]:
    headers = {}

    if "headers" in event and event["headers"]:
        for header_name, header_value in event["headers"].items():
            headers[header_name] = header_value

    # Multi value headers takes the precedence
    if "multiValueHeaders" in event and event["multiValueHeaders"]:
        for header_name, header_values in event["multiValueHeaders"].items():
            headers[header_name] = header_values

    # Set serverless related additional headers
    request_context = event.get("requestContext", {})
    if request_context.get("requestId"):
        headers["x-serverless-request-id"] = request_context.get("requestId")
    if request_context.get("stage"):
        headers["x-serverless-stage"] = request_context.get("stage")
    if headers.get("x-amzn-trace-id"):
        headers["x-serverless-trace-id"] = headers["x-amzn-trace-id"]

    return headers


def get_normalised_body_from_aws(event: AwsEvent) -> BytesIO:
    body = event.get("body", "")
    if event.get("isBase64Encoded", False):
        body = base64.b64decode(body)

    if isinstance(body, str):
        body = body.encode("utf-8")

    return BytesIO(body)


__all__ = [
    "AwsEvent",
    "AwsContext",
    "AwsServerlessFunction",
    "create_http_request_from_aws_event",
]
