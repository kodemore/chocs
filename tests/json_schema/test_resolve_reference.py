from os import path
from chocs.json_schema import OpenApiSchema


def test_can_open_json_schema_file() -> None:

    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    schema = OpenApiSchema(openapi_file)
    pet = schema["#/components/schemas/Pet"]

    print(pet)
