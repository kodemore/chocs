from chocs import HttpStatus


def test_http_status_str():
    status = HttpStatus.OK

    assert "200 OK" == str(status)
    assert 200 == int(status)
