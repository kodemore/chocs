from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus
from chocs import Application
from chocs import serve

app = Application()


@app.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.attributes['name']}!")


@app.get("*")
def default(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Not found", HttpStatus.NOT_FOUND)


serve(app)
