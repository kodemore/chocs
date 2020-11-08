import logging

from chocs import http
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@http.get("/users")
def get_users(request: HttpRequest) -> HttpResponse:
    logger.log("Hello AWS!")
    return HttpResponse(HttpStatus.OK, '{"test": true}', headers={"Test": "test header"})
