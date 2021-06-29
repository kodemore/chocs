import pytest
from os import path

from chocs.json_schema import (
    JsonReference,
    OpenApiSchema,
    URILoader,
    build_validator_from_schema,
)


def test_can_read_open_api_schema() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    schema = OpenApiSchema(openapi_file)

    assert "openapi" in schema
    assert schema["openapi"] == "3.0.0"


def test_can_query_open_api_schema() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    schema = OpenApiSchema(openapi_file)

    pet = schema.query("#/components/schemas/Pet")

    assert isinstance(pet, dict)
    assert "allOf" in pet

    assert isinstance(pet["allOf"][0], JsonReference)

    get_pet = schema.query("/paths/\\/pets/get")

    assert "operationId" in get_pet
    assert get_pet["operationId"] == "findPets"


def test_fails_on_invalid_query() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    schema = OpenApiSchema(openapi_file)

    with pytest.raises(KeyError):
        schema.query("/invalid/query")


def test_can_resolve_reference() -> None:
    loader = URILoader()
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    reference_id = openapi_file + "#/components/schemas/Pet"
    reference = JsonReference(reference_id, loader)

    assert "allOf" in reference
    assert len(reference["allOf"]) == 2

    assert repr(reference) == f"JsonReference({reference_id})"


def test_can_build_validator() -> None:
    openapi_file = path.realpath(path.dirname(__file__) + "/../fixtures/openapi.yml")
    schema = OpenApiSchema(openapi_file)

    pet = schema.query("#/components/schemas/Pet")
    validator = build_validator_from_schema(pet)

    assert validator({"name": "Bob", "id": 1})
    with pytest.raises(ValueError):
        validator({})
    with pytest.raises(ValueError):
        validator({"name": "Bob"})
    with pytest.raises(ValueError):
        validator({"id": 11})
    with pytest.raises(ValueError):
        validator({"name": 1, "id": 1})
