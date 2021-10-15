import pytest

from chocs import Application
from chocs.errors import ApplicationError


def test_can_load_dynamically_modules_with_const_ending() -> None:
    # given
    app = Application()

    # when
    app.use("tests.*.routes_a.*.routes")

    # then
    assert sorted(app._loaded_modules) == [
        "tests.fixtures.routes_a.a.routes",
        "tests.fixtures.routes_a.b.routes",
        "tests.fixtures.routes_a.c.routes",
    ]


def test_can_load_dynamically_modules_with_asterisk_ending() -> None:
    # given
    app = Application()

    # when
    app.use("tests.fixtures.routes.*")

    # then
    assert sorted(app._loaded_modules) == [
        "tests.fixtures.routes.a",
        "tests.fixtures.routes.b",
    ]


def test_will_fails_on_invalid_module_name() -> None:
    # given
    app = Application()

    # then
    with pytest.raises(ApplicationError):
        app.use("invalid.name")


