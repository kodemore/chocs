import json
import pytest
from copy import copy
from io import BytesIO
from typing import Union

from chocs import HttpHeaders, HttpMethod, HttpRequest


def test_can_instantiate() -> None:
    instance = HttpRequest(HttpMethod.GET)
    assert isinstance(instance, HttpRequest)


def test_get_cookies() -> None:
    instance = HttpRequest(
        HttpMethod.GET,
        headers=HttpHeaders({"cookie": "key=value; anotherkey=anothervalue"}),
    )
    cookies = instance.cookies

    assert len(cookies) == 2
    assert str(cookies["key"]) == "value"
    assert str(cookies["anotherkey"]) == "anothervalue"


def test_create_json_request() -> None:
    json_data = json.dumps({"test": "OK"}).encode("utf8")
    instance = HttpRequest(
        HttpMethod.GET,
        "/json",
        BytesIO(json_data),
        headers=HttpHeaders({"Content-Type": "application/json"}),
    )

    assert dict(instance.parsed_body) == {"test": "OK"}


@pytest.mark.parametrize(
    "a, b",
    [
        [HttpRequest(HttpMethod.GET), HttpRequest(HttpMethod.GET)],
        [
            HttpRequest(HttpMethod.GET, headers={"test": "1"}),
            HttpRequest(HttpMethod.GET, headers={"test": "1"}),
        ],
        [
            HttpRequest(HttpMethod.GET, path="/test/1"),
            HttpRequest(HttpMethod.GET, path="/test/1"),
        ],
    ],
)
def test_compare_equal_http_request(a: HttpRequest, b: HttpRequest) -> None:
    assert a == b


@pytest.mark.parametrize(
    "a, b",
    [
        [HttpRequest(HttpMethod.GET), HttpRequest(HttpMethod.POST)],
        [
            HttpRequest(HttpMethod.GET, headers={"test": "1"}),
            HttpRequest(HttpMethod.GET, headers={"test": "2"}),
        ],
        [
            HttpRequest(HttpMethod.GET, path="/test/2"),
            HttpRequest(HttpMethod.GET, path="/test/1"),
        ],
    ],
)
def test_compare_not_equal_http_request(a: HttpRequest, b: HttpRequest) -> None:
    assert not a == b


def test_http_request_as_str() -> None:
    body = '{"a": 1}'
    request = HttpRequest(HttpMethod.POST, body=body)

    assert request.as_str() == body
    assert request.as_str() == body


def test_http_request_as_dict() -> None:
    body = '{"a": 1}'
    request = HttpRequest(HttpMethod.POST, body=body)

    assert request.as_str() == body
    assert request.as_dict() == {"a": 1}


@pytest.mark.parametrize(
    "data, expected",
    [
        [b"example body", "example body"],
        [BytesIO(b"example body"), "example body"],
        ["example body", "example body"],
        [bytearray("example body", "utf8"), "example body"],
        [None, ""],
    ],
)
def test_http_request_body_type(
    data: Union[bytes, bytearray, BytesIO, str, None], expected: str
) -> None:
    request = HttpRequest(HttpMethod.GET, body=data)

    assert str(request) == expected


def test_can_copy() -> None:
    # given
    headers = {
        "Header-1": "value-1",
        "heaDer-2": 13,
    }
    request = HttpRequest(HttpMethod.GET, body=b"test body", headers=headers)

    # when
    request_copy = copy(request)
    assert request_copy == request
    request_copy.headers.set("header-1", "new-value")

    # then
    assert request.headers.get("header-1") == "value-1"
