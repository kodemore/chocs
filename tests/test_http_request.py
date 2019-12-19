from chocs import Headers
from chocs import HttpRequest


def test_can_instantiate():
    instance = HttpRequest("GET")
    assert isinstance(instance, HttpRequest)


def test_get_cookies():
    instance = HttpRequest("GET")
    instance.headers = Headers({"cookie": "key=value; anotherkey=anothervalue"})
    cookies = instance.cookies

    assert len(cookies) == 2
    assert cookies[0].name == "key"
    assert cookies[0].value == "value"
    assert cookies[1].name == "anotherkey"
    assert cookies[1].value == "anothervalue"
