import logging
import os

from chocs.application import http
from chocs.http_request import HttpRequest
from chocs.http_response import HttpResponse
from chocs.http_status import HttpStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@http.get("/users")
def get_users(request: HttpRequest) -> HttpResponse:
    return HttpResponse(HttpStatus.OK, '{"test": true}', headers={"Test": "test header"})
