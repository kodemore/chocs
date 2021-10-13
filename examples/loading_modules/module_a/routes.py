from chocs import HttpRequest, HttpResponse
from examples.loading_modules.app import app


@app.get("/hello-a/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello from module A: {request.path_parameters['name']}!")
