from chocs import Application
from chocs import HttpRequest
from chocs import HttpResponse
from chocs.serverless import create_serverless_handler

app = Application()


@app.get("/hello/{name}")
def hello_one(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello {request.path_parameters['name']}!")


@app.get("/hello2/{name}")
def hello_one(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Friend or foe? Oh its you {request.path_parameters['name']}, hello!")


test_handler = create_serverless_handler(app)
