from dataclasses import dataclass

import json
from os import path

from chocs import Application, HttpRequest, HttpResponse, HttpStatus, serve
from chocs.json_schema.errors import ValidationError
from chocs.middleware import OpenApiMiddleware

open_api_filename = path.dirname(__file__) + "/openapi.yml"


def error_handler(request, next) -> HttpResponse:
    try:
        return next(request)
    except ValidationError as error:
        json_error = {"error_code": error.code, "error_message": str(error)}
        return HttpResponse(
            json.dumps(json_error), status=HttpStatus.UNPROCESSABLE_ENTITY
        )


app = Application(error_handler, OpenApiMiddleware(open_api_filename))


@dataclass()
class Pet:
    id: str
    name: str


@app.post("/pets", parsed_body=Pet)
def create_pet(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.parsed_body, Pet)
    pet = request.parsed_body  # type: Pet

    return HttpResponse(pet.name)


serve(app, port=8080, debug=True)
