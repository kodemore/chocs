import json
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
