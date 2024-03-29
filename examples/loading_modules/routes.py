from chocs import HttpRequest, HttpResponse
from examples.loading_modules.app import app


@app.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.path_parameters['name']}!")
