from io import BytesIO

from chocs import HttpRequest
from chocs.message import JsonBody

test_wsgi_body = {
    "CONTENT_TYPE": "application/json; charset=utf-8",
    "REQUEST_METHOD": "POST",
    "wsgi.input": BytesIO(b'{"test_1":"1","test_2":"Test 2","test_3":"{test 3}"}'),
}


def test_json_body():
    request = HttpRequest.from_wsgi(test_wsgi_body)
    body = request.parsed_body

    assert isinstance(body, JsonBody)
    assert "test_1" in body
    assert body["test_1"] == "1"
    assert body.get("test2", "default") == "default"
