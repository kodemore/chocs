import re
from typing import Callable

import pytest

from chocs import HttpMethod
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus
from chocs import NotFoundError
from chocs import Route
from chocs import Router
from chocs import Application
from chocs import RouterMiddleware


def test_route_parsing() -> None:
    route = Route("/example/{pattern}")
    assert route.match("/example/test")


def test_route_parsing_with_wildcards() -> None:
    route = Route("/example/{a}*")
    assert route.pattern == re.compile(r"^/example/([^/]+).*?$", re.I | re.M)
    assert route.match("/example/test/1/2/3")
    assert route.match("/example/11")


def test_route_is_wildcard() -> None:
    route = Route("*")

    assert route.is_wildcard
    assert route.pattern == re.compile(r"^.*?$", re.I | re.M)


def test_route_match() -> None:
    route = Route("/pets/{pet_id}")
    route = route.match("/pets/11a22")
    assert route["pet_id"] == "11a22"

    route = Route("/pets/{pet_id}")
    route = route.match("/pets/22")
    assert route._parameters == {"pet_id": "22"}


def test_router() -> None:
    def test_controller() -> None:
        pass

    router = Router()
    router.append(Route("/pets/{pet_id}"), test_controller)
    router.append(Route("/pets"), test_controller)
    match = router.match("/pets/12")

    assert match[0]["pet_id"] == "12"
    assert router.match("/pets")


def test_router_fail_matching() -> None:
    def test_controller():
        pass

    router = Router()
    router.append(Route("/pets/{pet_id}"), test_controller)
    with pytest.raises(NotFoundError):
        router.match("/pet/12")


def test_route_match_multiple_parameters() -> None:
    route = Route("/pets/{pet_id}/{category}")
    route = route.match("/pets/11a22/test")
    assert route["pet_id"] == "11a22"
    assert route["category"] == "test"


def test_router_prioritise_routes_with_no_wildcards() -> None:
    def test_controller():
        pass

    router = Router()
    router.append(Route("/pets/*"), test_controller)
    router.append(Route("/pets/{pet_id}"), test_controller)
    router.append(Route("*"), test_controller)

    route, controller = router.match("/pets/11a22")

    assert route.route == "/pets/{pet_id}"


http = Application()


@pytest.mark.parametrize(
    "router_decorator, method",
    [
        (http.get, HttpMethod.GET),
        (http.post, HttpMethod.POST),
        (http.put, HttpMethod.PUT),
        (http.patch, HttpMethod.PATCH),
        (http.options, HttpMethod.OPTIONS),
        (http.delete, HttpMethod.DELETE),
        (http.head, HttpMethod.HEAD),
    ],
)
def test_router_method(router_decorator: Callable, method: HttpMethod) -> None:
    ok_response = HttpResponse("OK", HttpStatus.OK)
    request = HttpRequest(method, "/pet")
    router = RouterMiddleware()
    router.routes = http.routes

    def noop():
        pass

    @router_decorator("/pet")
    def get_pet(req: HttpRequest) -> HttpResponse:
        return ok_response

    assert get_pet(HttpRequest(HttpMethod.GET)) == ok_response
    assert router.handle(request, noop) == ok_response


def test_router_not_found() -> None:
    app = Application()

    request = HttpRequest(HttpMethod.GET, "/pet")
    response = app(request)

    assert response.status_code == HttpStatus.NOT_FOUND
