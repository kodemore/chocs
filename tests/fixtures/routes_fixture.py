from chocs import HttpRequest, HttpResponse, HttpStatus
from tests.fixtures.app_fixture import app


@app.get("/test")
def test_get(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test get")


@app.post("/test")
def test_patch(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test post")


@app.patch("/test")
def test_patch(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test patch")


@app.put("/test")
def test_patch(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test put")


@app.delete("/test")
def test_delete(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test delete")


@app.options("/test")
def test_delete(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test options")


@app.head("/test")
def test_delete(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=HttpStatus.OK, body="test head")
