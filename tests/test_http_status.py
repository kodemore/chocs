from chocs import HttpStatus


def test_http_status_str():
    status = HttpStatus.OK

    assert "200" == str(status)
