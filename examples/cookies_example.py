from datetime import datetime

from chocs import HttpCookie
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus
from chocs import Application
from chocs import serve


app = Application()


@app.get("/")
def default(request: HttpRequest) -> HttpResponse:
    """Shows how cookie work"""
    client_cookies = request.cookies

    response = HttpResponse("Not found", HttpStatus.NOT_FOUND)
    response.cookies["simple_cookie"] = "value"
    response.cookies.append(
        HttpCookie(
            "advanced_cookie", "Advanced value {test 1}", expires=datetime(2021, 1, 1)
        )
    )
    return response


serve(app, host="127.0.0.1", port=8080)
