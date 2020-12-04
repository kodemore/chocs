import pytest

from chocs import HttpCookie
from chocs import HttpHeaders
from chocs import HttpResponse
from chocs import HttpStatus


def test_can_instantiate() -> None:
    instance = HttpResponse(status=200)
    assert isinstance(instance, HttpResponse)


def test_can_write_and_read_body() -> None:
    instance = HttpResponse(status=200)
    instance.write("Example text")
    assert str(instance) == "Example text"
    instance.body.seek(0)
    assert instance.body.read() == b"Example text"


def test_can_close_body() -> None:
    instance = HttpResponse(status=HttpStatus.OK)
    instance.write("Test")
    assert instance.writable
    instance.close()
    assert not instance.writable


def test_headers() -> None:
    instance = HttpResponse()
    with pytest.raises(AttributeError):
        instance.headers = None

    assert isinstance(instance.headers, HttpHeaders)


def test_set_cookie() -> None:
    instance = HttpResponse()
    instance.cookies.append(HttpCookie("name", "value"))
    assert instance.headers.get("Set-Cookie") == "name=value"


def test_two_instances_are_equal() -> None:
    instance = HttpResponse()
    instance_2 = HttpResponse()

    
