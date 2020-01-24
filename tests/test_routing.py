import pytest
import re

from typing import Callable
from chocs.errors import NotFoundError
from chocs.routing import Route
from chocs.routing import Router
from chocs import HttpMethod, HttpRequest, HttpResponse, router


def test_route_parsing():
    route = Route("/example/{pattern}")
    assert route.match("/example/test")

    route = Route("/example/{pattern}", pattern=r"\d+")
    assert route.match("/example/12")
    assert not route.match("/example/fail")


def test_route_parsing_with_wildcards():
    route = Route("/example/{a}*")
    assert route.pattern == re.compile(r"^/example/([^/]+).*?$", re.I | re.M)
    assert route.match("/example/test/1/2/3")
    assert route.match("/example/11")


def test_route_is_wildcard():
    route = Route("*")

    assert route.wildcard
    assert route.pattern == re.compile(r"^.*?$", re.I | re.M)


def test_route_match():
    route = Route("/pets/{pet_id}")
    route = route.match("/pets/11a22")
    assert route["pet_id"] == "11a22"

    route = Route("/pets/{pet_id}", pet_id=r"\d+")
    assert not route.match("/pets/11a22")
    route = route.match("/pets/22")
    assert route._attributes == {"pet_id": "22"}


def test_router():
    def test_controller():
        pass

    router = Router()
    router.append(Route("/pets/{pet_id}"), test_controller)
    router.append(Route("/pets"), test_controller)
    match = router.match("/pets/12")

    assert match[0]["pet_id"] == "12"
    assert router.match("/pets")


def test_router_fail_matching():
    def test_controller():
        pass

    router = Router()
    router.append(Route("/pets/{pet_id}", pet_id="[a-z]+"), test_controller)
    with pytest.raises(NotFoundError):
        router.match("/pets/12")


def test_route_match_multiple_parameters():
    route = Route("/pets/{pet_id}/{category}")
    route = route.match("/pets/11a22/test")
    assert route["pet_id"] == "11a22"
    assert route["category"] == "test"


def test_router_prioritise_routes_with_no_wildcards():
    def test_controller():
        pass

    router = Router()
    router.append(Route("/pets/*"), test_controller)
    router.append(Route("/pets/{pet_id}"), test_controller)
    router.append(Route("*"), test_controller)

    route, controller = router.match("/pets/11a22")

    assert route.route == "/pets/{pet_id}"


@pytest.mark.parametrize(
    "router_decorator, method",
    [
        (router.get, HttpMethod.GET),
        (router.post, HttpMethod.POST),
        (router.put, HttpMethod.PUT),
        (router.patch, HttpMethod.PATCH),
        (router.options, HttpMethod.OPTIONS),
        (router.delete, HttpMethod.DELETE),
        (router.head, HttpMethod.HEAD),
    ],
)
def test_router_method(router_decorator: Callable, method: HttpMethod):

    ok_response = HttpResponse(200, "OK")
    request = HttpRequest(method, "/pet")

    def noop():
        pass

    @router_decorator("/pet")
    def get_pet(req: HttpRequest) -> HttpResponse:
        return ok_response

    assert get_pet(HttpRequest(HttpMethod.GET)) == ok_response
    assert router.handle(request, noop) == ok_response
