import json
import pytest
from io import BytesIO

from chocs import HttpHeaders, HttpMethod, HttpRequest


def test_can_instantiate() -> None:
    instance = HttpRequest(HttpMethod.GET)
    assert isinstance(instance, HttpRequest)


def test_get_cookies() -> None:
    instance = HttpRequest(HttpMethod.GET)
    instance.headers = HttpHeaders({"cookie": "key=value; anotherkey=anothervalue"})
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

    assert instance.parsed_body == {"test": "OK"}


@pytest.mark.parametrize('a, b', [
    [HttpRequest(HttpMethod.GET), HttpRequest(HttpMethod.GET)],
    [HttpRequest(HttpMethod.GET, headers={"test": "1"}), HttpRequest(HttpMethod.GET, headers={"test": "1"})],
    [HttpRequest(HttpMethod.GET, path="/test/1"), HttpRequest(HttpMethod.GET, path="/test/1")],
])
def test_compare_equal_http_request(a: HttpRequest, b: HttpRequest) -> None:
    assert a == b


@pytest.mark.parametrize('a, b', [
    [HttpRequest(HttpMethod.GET), HttpRequest(HttpMethod.POST)],
    [HttpRequest(HttpMethod.GET, headers={"test": "1"}), HttpRequest(HttpMethod.GET, headers={"test": "2"})],
    [HttpRequest(HttpMethod.GET, path="/test/2"), HttpRequest(HttpMethod.GET, path="/test/1")],
])
def test_compare_not_equal_http_request(a: HttpRequest, b: HttpRequest) -> None:
    assert not a == b
