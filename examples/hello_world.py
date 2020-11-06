from chocs import HttpRequest
from chocs import HttpStatus
from chocs import HttpResponse
from chocs import serve
from chocs import router


@router.get("/hello/{name}", name=r"\w+")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.attributes['name']}!")


@router.get("*")
def default(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpStatus.NOT_FOUND, "Not found")

