import json
from os import path

from chocs import Application, HttpMethod, HttpRequest, HttpResponse, HttpStatus
from chocs.middleware import OpenApiMiddleware
from chocs.json_schema import build_validator_from_schema


def test_validate_all_of_for_one_string() -> None:
    # given
    validator = build_validator_from_schema({
        "allOf": [
            {
                "type": "object",
                "properties": {
                    "flag": {
                        "type": "string",
                        "format": "boolean",
                    },
                    "name": {
                      "type": "string",
                    }
                }
            },
            {
                "type": "object",
                "properties": {
                    "flag": {
                        "type": "string",
                        "format": "boolean",
                    },
                    "id": {
                        "type": "number",
                    }
                }
            }
        ]
    })

    # when
    valid_data = validator({
        "flag": "true",
        "name": "dude",
        "id": 12
    })

    # then
    assert valid_data == {
        "flag": True,
        "name": "dude",
        "id": 12,
    }
