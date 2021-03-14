from chocs import Application, HttpRequest, HttpResponse, HttpStatus, serve
from chocs.wsgi import WsgiServers

app = Application()


@app.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.path_parameters['name']}!")


@app.get("*")
def default(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Not found", HttpStatus.NOT_FOUND)


serve(app, port=8080, debug=True, wsgi_server=WsgiServers.CHERRYPY)
