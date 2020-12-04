import pytest

from chocs import HttpHeaders


def test_can_instantiate():
    headers = HttpHeaders()
    assert isinstance(headers, HttpHeaders)


def test_normalize_wsgi_headers():
    headers = HttpHeaders(
        {"HTTP_USER_AGENT": "Test Agent", "HTTP_ACCEPT": "plain/text"}
    )

    assert headers["User-Agent"] == "Test Agent"
    assert headers["HTTP_USER_AGENT"] == "Test Agent"
    assert headers["USER_AGENT"] == "Test Agent"
    assert headers["USER-AGENT"] == "Test Agent"
    assert headers.get("User-Agent") == "Test Agent"


def test_add_header():
    headers = HttpHeaders()
    headers.set("USER_AGENT", "Test Agent")
    assert headers["HTTP_USER_AGENT"] == "Test Agent"
    assert headers["USER_AGENT"] == "Test Agent"
    assert headers["USER-AGENT"] == "Test Agent"
    assert headers.get("User-Agent") == "Test Agent"


def test_non_unique_headers():
    headers = HttpHeaders()
    headers.set("Set-Cookie", "123")
    headers.set("Set-Cookie", "456")
    headers.set("Set-Cookie", "789")

    assert headers["Set-Cookie"] == [
        "123",
        "456",
        "789",
    ]

    # test items view
    assert [(key, value) for key, value in headers.items()] == [
        ("set-cookie", "123"),
        ("set-cookie", "456"),
        ("set-cookie", "789"),
    ]


def test_eq_headers() -> None:
    headers = HttpHeaders()
    headers_copy = HttpHeaders()

    assert headers == headers_copy

    headers['test'] = 'value'
    headers_copy['test'] = 'value'

    assert headers == headers_copy

    headers_copy['test_2'] = 'value'

    assert not headers == headers_copy
