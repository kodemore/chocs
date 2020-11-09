from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus
from chocs import http
from chocs import serve


@http.get("/hello/{name}", name=r"\w+")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.attributes['name']}!")


@http.get("*")
def default(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpStatus.NOT_FOUND, "Not found")


serve()
