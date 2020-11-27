from chocs.json_schema import SchemaValidator
from os import path


OPENAPI_FILENAME = path.join(path.dirname(__file__), 'fixtures', 'openapi.yml')


def test_can_read_openapi_file():
    validator_factory = SchemaValidator(OPENAPI_FILENAME)

    assert "openapi" in validator_factory.openapi
    assert "info" in validator_factory.openapi


def test_can_create_schema_validator_from_openapi_file():
    validator_factory = SchemaValidator(OPENAPI_FILENAME)

    schema_validator = validator_factory.create_validator('#/components/schemas/Pet')

    schema_validator({'a': 1})


def test_dict_reference():
    dict_a = {}

    dict_a['a'] = {
        'a': 1,
        'b': 2,
        'ref': {}
    }

    dict_a['a']['ref'] = dict_a

    a = 1
