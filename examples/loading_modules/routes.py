from app import app
from chocs import HttpRequest, HttpResponse


@app.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.path_parameters['name']}!")
