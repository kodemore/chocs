import pytest

from chocs import (
    HttpCookie,
    HttpHeaders,
    HttpMessage,
    HttpResponse,
    HttpStatus,
    JsonHttpMessage,
)


def test_can_instantiate() -> None:
    instance = HttpResponse(status=200)
    assert isinstance(instance, HttpResponse)


def test_can_write_and_read_body() -> None:
    instance = HttpResponse(status=200)
    instance.write("Example text")
    assert str(instance) == "Example text"
    instance.body.seek(0)
    assert instance.body.read() == b"Example text"


def test_can_close_body() -> None:
    instance = HttpResponse(status=HttpStatus.OK)
    instance.write("Test")
    assert instance.writable
    instance.close()
    assert not instance.writable


def test_headers() -> None:
    instance = HttpResponse()
    with pytest.raises(AttributeError):
        instance.headers = None

    assert isinstance(instance.headers, HttpHeaders)


def test_set_cookie() -> None:
    instance = HttpResponse()
    instance.cookies.append(HttpCookie("name", "value"))
    assert instance.headers.get("Set-Cookie") == "name=value"


@pytest.mark.parametrize(
    "instance, instance_copy",
    [
        [HttpResponse(), HttpResponse()],
        [HttpResponse(status=HttpStatus.OK), HttpResponse(status=HttpStatus.OK)],
        [HttpResponse(headers={"test": "1"}), HttpResponse(headers={"test": "1"})],
        [HttpResponse(encoding="iso-8859-1"), HttpResponse(encoding="iso-8859-1")],
        [
            HttpResponse(body="test 1"),
            HttpResponse(body="test 2"),
        ],  # HttpResponse only compares size of bodies not the exact values
        [
            HttpResponse(
                status=HttpStatus.OK, headers={"test": "1"}, encoding="iso-8859-1"
            ),
            HttpResponse(
                status=HttpStatus.OK, headers={"test": "1"}, encoding="iso-8859-1"
            ),
        ],
    ],
)
def test_two_response_instances_are_equal(
    instance: HttpResponse, instance_copy: HttpResponse
) -> None:

    assert instance == instance_copy


@pytest.mark.parametrize(
    "instance, instance_copy",
    [
        [HttpResponse(), HttpResponse(status=HttpStatus.CREATED)],
        [
            HttpResponse(status=HttpStatus.OK),
            HttpResponse(status=HttpStatus.OK, headers={"test": "1"}),
        ],
        [HttpResponse(), HttpResponse(encoding="iso-8859-2")],
        [HttpResponse(), HttpResponse(body="iso-8859-2")],
    ],
)
def test_two_response_instances_are_different(
    instance: HttpResponse, instance_copy: HttpResponse
) -> None:

    assert not instance == instance_copy


def test_http_response_as_str() -> None:
    body = '{"a": 1}'
    response = HttpResponse(body)

    assert response.as_str() == body
    assert response.as_str() == body


def test_http_response_as_dict() -> None:
    body = '{"a": 1}'
    response = HttpResponse(body)

    assert response.as_str() == body
    assert response.as_dict() == {"a": 1}


def test_http_response_parsed_body_as_json_message() -> None:
    body = '{"a": 1}'
    response = HttpResponse(body=body, headers={"content-type": "application/json"})

    assert isinstance(response.parsed_body, JsonHttpMessage)
