from io import BytesIO

from chocs import FormHttpMessage, HttpRequest, JsonHttpMessage, MultipartHttpMessage, UploadedFile, SimpleHttpMessage

multipart_body = {
    "CONTENT_TYPE": "multipart/form-data; charset=utf-8; boundary=__TEST_BOUNDARY__",
    "REQUEST_METHOD": "POST",
    "wsgi.input": BytesIO(
        b"--__TEST_BOUNDARY__\r\n"
        b'Content-Disposition: form-data; name="id"\r\n\r\n'
        b"51b8a72aaaf909e303000034\r\n"
        b"--__TEST_BOUNDARY__\r\n"
        b'Content-Disposition: form-data; name="file_a"; filename="orange.gif"\r\n'
        b"Content-Type: image/gif\r\n\r\n"
        b"GIF87a\x02\x00\x02\x00\x91\x00\x00\x00\x00\x00\xff\x8c\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\t\x00"
        b"\x00\x03\x00,\x00\x00\x00\x00\x02\x00\x02\x00\x00\x02\x02\x8cS\x00;\r\n"
        b"--__TEST_BOUNDARY__\r\n"
        b'Content-Disposition: form-data; name="file_b"; filename="yellow.gif"\r\n'
        b"Content-Type: image/gif\r\n\r\n"
        b"GIF87a\x02\x00\x02\x00\x91\x00\x00\x00\x00\x00\xff\xf6~\xff\xff\xff\x00\x00\x00!\xf9\x04\t\x00\x00"
        b"\x03\x00,\x00\x00\x00\x00\x02\x00\x02\x00\x00\x02\x02\x8cS\x00;\r\n"
        b"--__TEST_BOUNDARY__\r\n"
        b'Content-Disposition: form-data; name="test_1"\r\n\r\n'
        b"only string value\r\n"
        b"--__TEST_BOUNDARY__\r\n"
        b'Content-Disposition: form-data; name="test_2"\r\n\r\n'
        b"1232\r\n"
        b"--__TEST_BOUNDARY__--\r\n"
    ),
}

form_body = {
    "CONTENT_TYPE": "application/x-www-form-urlencoded; charset=utf-8",
    "REQUEST_METHOD": "POST",
    "wsgi.input": BytesIO(b"test_1=1&test_2=Test+2&test_3=%7Btest+3%7D"),
}

json_body = {
    "CONTENT_TYPE": "application/json; charset=utf-8",
    "REQUEST_METHOD": "POST",
    "wsgi.input": BytesIO(b'{"test_1":"1","test_2":"Test 2","test_3":"{test 3}"}'),
}


def test_parse_multipart_body() -> None:
    request = HttpRequest(
        multipart_body["REQUEST_METHOD"],
        body=multipart_body["wsgi.input"],
        headers={"content-type": multipart_body["CONTENT_TYPE"]},
    )
    body = request.parsed_body
    assert isinstance(body, MultipartHttpMessage)
    assert str(body["id"]) == "51b8a72aaaf909e303000034"
    assert str(body["test_1"]) == "only string value"
    assert str(body["test_2"]) == "1232"
    assert isinstance(body["file_a"], UploadedFile)
    assert isinstance(body["file_b"], UploadedFile)
    assert body["file_a"].filename == "orange.gif"
    assert body["file_b"].filename == "yellow.gif"
    assert body.get("test2", "default") == "default"
    assert len(body["file_a"]) == 49


def test_parse_form_body() -> None:
    request = HttpRequest(
        form_body["REQUEST_METHOD"],
        body=form_body["wsgi.input"],
        headers={"content-type": form_body["CONTENT_TYPE"]},
    )
    body = request.parsed_body
    assert isinstance(body, FormHttpMessage)
    assert str(body["test_1"]) == "1"
    assert body.get("test2", "default") == "default"


def test_parse_json_body() -> None:
    request = HttpRequest(
        json_body["REQUEST_METHOD"],
        body=json_body["wsgi.input"],
        headers={"content-type": json_body["CONTENT_TYPE"]},
    )
    body = request.parsed_body

    assert isinstance(body, JsonHttpMessage)
    assert "test_1" in body
    assert body["test_1"] == "1"
    assert body.get("test2", "default") == "default"


def test_simple_http_message() -> None:
    http_message = SimpleHttpMessage("Hello World!")

    assert http_message[0:5] == "Hello"
    assert http_message == "Hello World!"
    assert http_message.upper() == "HELLO WORLD!"
    assert isinstance(http_message, SimpleHttpMessage)
