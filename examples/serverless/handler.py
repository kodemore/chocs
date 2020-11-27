import logging

from app import app

from chocs import HttpRequest
from chocs import HttpResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@app.get("/users")
def test_handler(request: HttpRequest) -> HttpResponse:
    logger.info("Hello AWS!")
    logger.info(request.attributes.get("aws_context"))
    logger.info(request.attributes.get("aws_event"))

    return HttpResponse('{"test": true}', headers={"Test": "test header"})


__all__ = ["test_handler"]
