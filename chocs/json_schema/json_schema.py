import yaml
from collections import UserDict
from jsonschema import Draft7Validator, RefResolver
from numbers import Number
from typing import Dict, List, Union


class SchemaStorage(UserDict):
    ...


class ReferenceResolver:
    def __init__(self, file_name: str, schema_storage: SchemaStorage):
        ...

    def resolve(self, reference: str) -> dict:
        ...
