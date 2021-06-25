import pytest

from chocs.json_schema import build_validator_from_schema
from chocs.json_schema.errors import ValidationError


def test_can_build_validator_for_nested_structures() -> None:
    validate = build_validator_from_schema({
        "type": "object",
        "properties": {
            "nested": {
                "oneOf": [
                    {
                        "type": "object",
                        "required": ["id"],
                        "properties": {
                            "id": {
                                "type": "string"
                            }
                        }
                    },
                    {
                        "type": "object",
                        "required": ["email"],
                        "properties": {
                            "email": {
                                "type": "string",
                                "format": "email",
                            }
                        }
                    }
                ]
            }
        }
    })

    assert validate({
        "nested": {
            "id": "some id"
        }
    })
    assert validate({
        "nested": {
            "email": "email@domain.com"
        }
    })
    
    with pytest.raises(ValidationError):
        validate({
            "nested": {
                "email": 12,
            }
        })
