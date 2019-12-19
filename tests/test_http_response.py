import pytest

from chocs import Headers
from chocs import HttpResponse
from chocs.cookies import Cookie


def test_can_instantiate():
    instance = HttpResponse(200)
    assert isinstance(instance, HttpResponse)


def test_can_write_and_read_body():
    instance = HttpResponse(200)
    instance.write("Example text")
    assert str(instance) == "Example text"
    instance.body.seek(0)
    assert instance.body.read() == b"Example text"


def test_can_close_body():
    instance = HttpResponse(200)
    instance.write("Test")
    assert instance.writable
    instance.close()
    assert not instance.writable


def test_headers():
    instance = HttpResponse()
    with pytest.raises(AttributeError):
        instance.headers = None

    assert isinstance(instance.headers, Headers)


def test_set_cookie():
    instance = HttpResponse()
    instance.cookies.append(Cookie("name", "value"))
    assert instance.headers.get("Set-Cookie") == "name=value"
