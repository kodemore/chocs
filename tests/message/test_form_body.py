from io import BytesIO

from chocs import HttpRequest
from chocs.message import FormBody

test_wsgi_body = {
    "CONTENT_TYPE": "application/x-www-form-urlencoded; charset=utf-8",
    "REQUEST_METHOD": "POST",
    "wsgi.input": BytesIO(b"test_1=1&test_2=Test+2&test_3=%7Btest+3%7D"),
}


def test_post_body():
    request = HttpRequest.from_wsgi(test_wsgi_body)
    body = request.parsed_body
    assert isinstance(body, FormBody)
    assert str(body["test_1"]) == "1"
    assert body.get("test2", "default") == "default"
