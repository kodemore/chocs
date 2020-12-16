from dataclasses import dataclass

from chocs import HttpApplication, HttpRequest, HttpResponse

app = HttpApplication(openapi="./openapi.yml")


@dataclass()
class Pet:
    id: str
    name: str


@app.post("/pets", map_to=Pet)
def create_pet(request: HttpRequest) -> HttpResponse:
    pet = request.parsed_body  # type: Pet
