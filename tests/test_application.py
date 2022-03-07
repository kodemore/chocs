import pytest
from inspect import signature

from chocs import Application, HttpMethod, HttpRequest, HttpResponse
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


def test_if_function_is_properly_wrapped() -> None:
    # given
    app = Application()

    @app.get("/pets")
    def get_pet(req: HttpRequest) -> HttpResponse:
        return HttpResponse("pet")

    # then
    assert get_pet.__name__ == "get_pet"
    func_sig = signature(get_pet)
    assert list(func_sig.parameters.keys()) == ["req"]


def test_if_request_is_containing_a_handler_name() -> None:
    # given
    app = Application()

    @app.get("/pets")
    def get_pet(req: HttpRequest) -> HttpResponse:
        assert req.attributes["handler_name"] == "get_pet"
        return HttpResponse("pet")
