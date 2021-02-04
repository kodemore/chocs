from dataclasses import dataclass

from chocs import Application, HttpRequest, HttpResponse, HttpStatus, serve
from chocs.middleware import ParsedBodyMiddleware


def error_handler(request, next) -> HttpResponse:
    try:
        return next(request)
    except Exception:
        return HttpResponse(
            body=str(HttpStatus.INTERNAL_SERVER_ERROR),
            status=HttpStatus.INTERNAL_SERVER_ERROR
        )


# in non strict mode object's initialiser is ignored
app = Application(error_handler, ParsedBodyMiddleware(strict=False))


@dataclass()
class Pet:
    id: str
    name: str


@app.post("/pets", parsed_body=Pet, strict=False)  # strict mode can be overridden for specific endpoint
def create_pet(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.parsed_body, Pet)
    pet = request.parsed_body  # type: Pet

    return HttpResponse(pet.name)


serve(app, port=8080, debug=True)
