import time

from chocs import HttpApplication
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import serve
from chocs.middleware import MiddlewareHandler


def time_load_middleware(request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
    started_at = time.time()
    response = next(request)
    total_time = (time.time() - started_at) * 100

    response.write(f"\nTotal time taken for generating response: {total_time}")

    return response


app = HttpApplication(time_load_middleware)


@app.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.attributes['name']}!")


serve(app)
