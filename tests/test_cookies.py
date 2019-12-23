from chocs.cookie_jar import CookieJar, Cookie
import pytest
from datetime import datetime


def test_can_instantiate():
    jar = CookieJar()
    assert isinstance(jar, CookieJar)


def test_set_simple_cookie():
    jar = CookieJar()
    jar["test"] = "value"

    assert "test" in jar
    assert isinstance(jar["test"], Cookie)
    assert "value" == str(jar["test"])


def test_set_cookie():
    jar = CookieJar()
    jar.append(Cookie("test", "value"))

    assert "test" in jar
    assert isinstance(jar["test"], Cookie)
    assert "value" == str(jar["test"])


def test_override_cookie():
    cookie = Cookie("test", "value")
    jar = CookieJar()
    jar["test"] = "value"
    jar.append(cookie)

    assert jar["test"] is cookie

    jar["test"] = "123"
    assert jar["test"] is not cookie


def test_fail_to_change_cookie_name():
    jar = CookieJar()
    jar["test"] = "name"
    cookie = jar["test"]

    with pytest.raises(AttributeError):
        cookie.name = "test-2"


@pytest.mark.parametrize(
    "cookie,expected",
    [
        (Cookie("name", "value"), "name=value"),
        (
            Cookie("name", "value", expires=datetime(1999, 1, 1)),
            "name=value; Expires=Fri, 01 Jan 1999 00:00:00 ",
        ),
        (Cookie("name", "value", http_only=True), "name=value; HttpOnly"),
        (Cookie("name", "value", secure=True), "name=value; Secure"),
        (
            Cookie("name", "value", secure=True, http_only=True),
            "name=value; Secure; HttpOnly",
        ),
        (
            Cookie("name", "value", secure=True, same_site=True),
            "name=value; Secure; SameSite=Strict",
        ),
        (
            Cookie(
                "name",
                "value",
                secure=True,
                same_site=True,
                expires=datetime(1999, 1, 1),
            ),
            "name=value; Expires=Fri, 01 Jan 1999 00:00:00 ; Secure; SameSite=Strict",
        ),
    ],
)
def test_serialise_cookie(cookie: Cookie, expected: str):
    assert cookie.serialise() == expected
