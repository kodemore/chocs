from collections import UserDict
from numbers import Number
from typing import Dict
from typing import List
from typing import Union

import yaml
from jsonschema import Draft7Validator
from jsonschema import RefResolver


class SchemaStorage(UserDict):
    ...


class ReferenceResolver:
    def __init__(self, file_name: str, schema_storage: SchemaStorage):
        ...

    def resolve(self, reference: str) -> dict:
        ...
