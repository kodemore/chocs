from chocs import HttpStatus


def test_http_status_str() -> None:
    status = HttpStatus.OK

    assert "200 OK" == str(status)
    assert 200 == int(status)


def test_http_status_from_int() -> None:
    status = HttpStatus.from_int(200)

    assert "200 OK" == str(status)
    assert 200 == int(status)


def test_http_status_operators() -> None:
    assert HttpStatus.OK > 100
    assert HttpStatus.OK > HttpStatus.CONTINUE
    assert HttpStatus.OK >= 200
    assert HttpStatus.OK >= HttpStatus.OK
    assert HttpStatus.OK == HttpStatus.OK
    assert HttpStatus.OK == 200
    assert HttpStatus.CONTINUE < 200
    assert HttpStatus.CONTINUE <= 100
    assert HttpStatus.CONTINUE <= HttpStatus.CONTINUE
    assert HttpStatus.CONTINUE == HttpStatus.CONTINUE
    assert HttpStatus.CONTINUE == 100
