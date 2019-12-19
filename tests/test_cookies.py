from datetime import datetime

from chocs.cookies import Cookie
from chocs.cookies import CookieParser


def test_can_instantiate():
    headers = Cookie("key", "value")
    assert isinstance(headers, Cookie)


def test_cookie_as_string():
    assert str(Cookie("key", "value", "test.com", "/", datetime(2020, 5, 17))) == (
        "Set-Cookie: key=value; Domain=/; expires=Sun, 17 May 2020 00:00:00 GMT; "
        "Path=test.com"
    )


def test_cookie_as_header():
    instance = Cookie("key", "value", "test.com", "/", datetime(2020, 5, 17))
    header, value = instance.header()
    assert header == "Set-Cookie"
    assert (
        value
        == "key=value; Domain=/; expires=Sun, 17 May 2020 00:00:00 GMT; Path=test.com"
    )


def test_cookies_from_header():
    header = "session=encodedguff; token=somehash"
    instance = CookieParser(header)
    cookies = instance.to_list()
    assert len(cookies) == 2
    assert cookies[0].name == "session"
    assert cookies[0].value == "encodedguff"
    assert cookies[1].name == "token"
    assert cookies[1].value == "somehash"
