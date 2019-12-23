from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus
from chocs import Cookie
from chocs import router
from chocs import serve
from datetime import datetime


@router.get("*")
def default(request: HttpRequest) -> HttpResponse:
    """Shows how cookie work"""
    client_cookies = request.cookies

    response = HttpResponse(HttpStatus.NOT_FOUND, "Not found")
    response.cookies["simple_cookie"] = "value"
    response.cookies.append(
        Cookie(
            "advanced_cookie", "Advanced value {test 1}", expires=datetime(2021, 1, 1)
        )
    )
    return response


serve(host="127.0.0.1", port=8080)
