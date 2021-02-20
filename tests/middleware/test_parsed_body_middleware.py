from dataclasses import dataclass

import json
import pytest

from chocs import Application, HttpMethod, HttpRequest, HttpResponse
from chocs.middleware import ParsedBodyMiddleware


@dataclass
class Pet:
    name: str
    tag: str
    id: str


def _mockup_pet_endpoint(app: Application) -> None:
    @app.post("/pets", parsed_body=Pet)
    def create_pet(request: HttpRequest) -> HttpResponse:
        pet = request.parsed_body  # type: Pet
        assert isinstance(pet, Pet)
        return HttpResponse(pet.name)


def test_hydrate_parsed_body_with_strict_mode() -> None:
    app = Application(ParsedBodyMiddleware(strict=True))
    _mockup_pet_endpoint(app)
    invalid_body = json.dumps(
        {"name": "Bobek", "tag": "test", "id": 1, "unknown_property": "unknown_value"}
    )

    with pytest.raises(TypeError):
        app(
            HttpRequest(
                HttpMethod.POST,
                "/pets",
                body=invalid_body,
                headers={"content-type": "application/json"},
            )
        )

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


def test_hydrate_parsed_body_without_strict_mode() -> None:
    app = Application(ParsedBodyMiddleware(strict=False))
    _mockup_pet_endpoint(app)

    invalid_body = json.dumps(
        {"name": "Bobek", "tag": "test", "id": 1, "unknown_property": "unknown_value"}
    )

    respone = app(
        HttpRequest(
            HttpMethod.POST,
            "/pets",
            body=invalid_body,
            headers={"content-type": "application/json"},
        )
    )
    assert str(respone) == "Bobek"

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
