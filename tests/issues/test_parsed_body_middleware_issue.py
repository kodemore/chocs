import json
from dataclasses import dataclass
from os import path

from chocs import Application, HttpMethod, HttpRequest, HttpResponse
from chocs.middleware import OpenApiMiddleware, ParsedBodyMiddleware


@dataclass
class Pet:
    name: str
    tag: str
    id: str


def _mockup_pet_endpoint(app: Application) -> None:
    @app.post("/pets", parsed_body=Pet)
    def create_pet(request: HttpRequest) -> HttpResponse:
        pet: Pet = request.parsed_body
        assert isinstance(pet, Pet)
        return HttpResponse(pet.name)


def test_parsed_body_issue_when_not_composite_message() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    app = Application(OpenApiMiddleware(openapi_file), ParsedBodyMiddleware(strict=True))
    _mockup_pet_endpoint(app)
    valid_body = json.dumps({"name": "Bobek", "tag": "test", "id": 1,})
    response = app(
        HttpRequest(
            HttpMethod.POST,
            "/pets",
            body=valid_body,
            headers={"content-type": "application/json"},
        )
    )
    assert str(response) == "Bobek"

