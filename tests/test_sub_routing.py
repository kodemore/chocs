from chocs import Application, HttpMethod, HttpRequest, HttpResponse, HttpStatus


def test_can_define_sub_groups() -> None:

    app = Application()

    # /group_a
    with app.group("/group_a") as group_a:

        # /group_a/one
        @group_a.get("/one")
        def one(request: HttpRequest) -> HttpResponse:
            return HttpResponse("group a.1", status=200)

        # /group_a/two
        @group_a.get("/two")
        def two(request: HttpRequest) -> HttpResponse:
            return HttpResponse("group a.2", status=200)

        # /group_a/three
        with group_a.group("/three") as group_a_subgroup:
            # /group_a/three/one
            @group_a_subgroup.get("/one")
            def three(request: HttpRequest) -> HttpResponse:
                return HttpResponse("group a.3.1", status=200)

    # /group_b
    with app.group("/group_b") as group_b:

        # /group_b/one
        @group_b.get("/one")
        def one(request: HttpRequest) -> HttpResponse:
            return HttpResponse("group b.1", status=200)

    request = HttpRequest(HttpMethod.GET, "/group_a/one")

    response = app(request)
    assert str(response) == "group a.1"

    response = group_a(request)
    assert str(response) == "group a.1"

    response = group_b(request)
    assert response.status_code == HttpStatus.NOT_FOUND

    request = HttpRequest(HttpMethod.GET, "/group_b/one")

    response = app(request)
    assert str(response) == "group b.1"
