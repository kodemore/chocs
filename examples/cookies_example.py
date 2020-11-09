from datetime import datetime

from chocs import HttpCookie
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus
from chocs import http
from chocs import serve


@http.get("*")
def default(request: HttpRequest) -> HttpResponse:
    """Shows how cookie work"""
    client_cookies = request.cookies

    response = HttpResponse(HttpStatus.NOT_FOUND, "Not found")
    response.cookies["simple_cookie"] = "value"
    response.cookies.append(
        HttpCookie(
            "advanced_cookie", "Advanced value {test 1}", expires=datetime(2021, 1, 1)
        )
    )
    return response


serve(host="127.0.0.1", port=8080)
