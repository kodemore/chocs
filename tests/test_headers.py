from chocs.headers import Headers


def test_can_instantiate():
    headers = Headers()
    assert isinstance(headers, Headers)


def test_normalize_wsgi_headers():
    headers = Headers({"HTTP_USER_AGENT": "Test Agent", "HTTP_ACCEPT": "plain/text"})

    assert headers["User-Agent"] == "Test Agent"
    assert headers["HTTP_USER_AGENT"] == "Test Agent"
    assert headers["USER_AGENT"] == "Test Agent"
    assert headers["USER-AGENT"] == "Test Agent"
    assert headers.get("User-Agent") == "Test Agent"


def test_add_header():
    headers = Headers()
    headers.add_header("USER_AGENT", "Test Agent")
    assert headers["HTTP_USER_AGENT"] == "Test Agent"
    assert headers["USER_AGENT"] == "Test Agent"
    assert headers["USER-AGENT"] == "Test Agent"
    assert headers.get("User-Agent") == "Test Agent"
