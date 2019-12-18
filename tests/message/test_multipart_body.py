from io import BytesIO

from chocs import HttpRequest
from chocs.message import MultipartBody
from chocs.message.multipart_body import UploadedFile

test_wsgi_body = {
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


def test_multipart_body():
    request = HttpRequest.from_wsgi(test_wsgi_body)
    body = request.parsed_body
    assert isinstance(body, MultipartBody)
    assert str(body["id"]) == "51b8a72aaaf909e303000034"
    assert str(body["test_1"]) == "only string value"
    assert str(body["test_2"]) == "1232"
    assert isinstance(body["file_a"], UploadedFile)
    assert isinstance(body["file_b"], UploadedFile)
    assert body["file_a"].filename == "orange.gif"
    assert body["file_b"].filename == "yellow.gif"
    assert body.get("test2", "default") == "default"
    assert len(body["file_a"]) == 49
