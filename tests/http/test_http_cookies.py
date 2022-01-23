from copy import copy

import pytest
from datetime import datetime

from chocs import HttpCookie, HttpCookieJar


def test_can_instantiate():
    jar = HttpCookieJar()
    assert isinstance(jar, HttpCookieJar)


def test_set_simple_cookie():
    jar = HttpCookieJar()
    jar["test"] = "value"

    assert "test" in jar
    assert isinstance(jar["test"], HttpCookie)
    assert "value" == str(jar["test"])


def test_set_cookie():
    jar = HttpCookieJar()
    jar.append(HttpCookie("test", "value"))

    assert "test" in jar
    assert isinstance(jar["test"], HttpCookie)
    assert "value" == str(jar["test"])


def test_override_cookie():
    cookie = HttpCookie("test", "value")
    jar = HttpCookieJar()
    jar["test"] = "value"
    jar.append(cookie)

    assert jar["test"] is cookie

    jar["test"] = "123"
    assert jar["test"] is not cookie


def test_fail_to_change_cookie_name():
    jar = HttpCookieJar()
    jar["test"] = "name"
    cookie = jar["test"]

    with pytest.raises(AttributeError):
        cookie.name = "test-2"


@pytest.mark.parametrize(
    "cookie,expected",
    [
        (HttpCookie("name", "value"), "name=value"),
        (
            HttpCookie("name", "value", expires=datetime(1999, 1, 1)),
            "name=value; Expires=Fri, 01 Jan 1999 00:00:00 ",
        ),
        (HttpCookie("name", "value", http_only=True), "name=value; HttpOnly"),
        (HttpCookie("name", "value", secure=True), "name=value; Secure"),
        (
            HttpCookie("name", "value", secure=True, http_only=True),
            "name=value; Secure; HttpOnly",
        ),
        (
            HttpCookie("name", "value", secure=True, same_site=True),
            "name=value; Secure; SameSite=Strict",
        ),
        (
            HttpCookie(
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
def test_serialise_cookie(cookie: HttpCookie, expected: str):
    assert cookie.serialise() == expected


def test_can_copy_http_jar() -> None:
    # given
    jar = HttpCookieJar()
    jar.append(HttpCookie("test", "test"))

    # when
    jar_copy = copy(jar)
    jar_copy["test"] = "test-2"

    # then
    assert jar["test"] == "test"
    assert jar_copy["test"] == "test-2"
