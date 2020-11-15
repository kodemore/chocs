import logging

from chocs import http
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import HttpStatus

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@http.get("/users", schema="/cos/ta/user.json")
def test_handler(request: HttpRequest) -> HttpResponse:
    logger.info("Hello AWS!")
    logger.info(request.attributes.get("aws_context"))
    logger.info(request.attributes.get("aws_event"))
    request.parsed_body
    return HttpResponse(HttpStatus.OK, '{"test": true}', headers={"Test": "test header"})


__all__ = ["test_handler"]
