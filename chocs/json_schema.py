from collections import UserDict
from numbers import Number
from typing import Dict
from typing import List
from typing import Union

import yaml
from jsonschema import Draft7Validator
from jsonschema import RefResolver


class SchemaItem:
    title: str
    description: str
    type: str


class Aggregator:
    all_of: List[SchemaItem]
    any_of: List[SchemaItem]
    one_of: List[SchemaItem]
    not_like: List[SchemaItem]


class BooleanType(SchemaItem):
    type = "boolean"


class StringType(SchemaItem):
    type = "string"
    min_length: int
    max_length: int
    format: str
    pattern: str


class EnumType(SchemaItem):
    enum: List[Union[str, int, float, Number, bool, type(None)]]


class ObjectType(SchemaItem):
    type = "object"
    required_properties: List[str]
    properties: Dict[str, SchemaItem]
    additional_properties: bool
    min_properties: int
    max_properties: int
    property_names: List[StringType]


class IntegerType(SchemaItem):
    type = "integer"
    multiple_of: int
    exclusive_minimum: int
    exclusive_maximum: int
    inclusive_minimum: int
    inclusive_maximum: int

    @property
    def minimum(self) -> int:
        return self.exclusive_minimum

    @minimum.setter
    def minimum(self, value: int) -> None:
        self.exclusive_minimum = value

    @property
    def maximum(self) -> int:
        return self.exclusive_maximum

    @maximum.setter
    def maximum(self, value: int) -> None:
        self.exclusive_maximum = value


class NumberType(SchemaItem):
    type = "number"
    multiple_of: Number
    exclusive_minimum: Number
    exclusive_maximum: Number
    inclusive_minimum: Number
    inclusive_maximum: Number

    @property
    def minimum(self) -> Number:
        return self.exclusive_minimum

    @minimum.setter
    def minimum(self, value: Number) -> None:
        self.exclusive_minimum = value

    @property
    def maximum(self) -> Number:
        return self.exclusive_maximum

    @maximum.setter
    def maximum(self, value: Number) -> None:
        self.exclusive_maximum = value


class ArrayType(SchemaItem):
    type = "array"
    item_type: Union[SchemaItem, List[SchemaItem]]
    minimum_items: int
    maximum_items: int
    unique_items: bool


class SchemaStorage(UserDict):
    ...


class ReferenceResolver(RefResolver):
    def __init__(self, base_uri, referrer):
        super().__init__(base_uri, referrer, SchemaStorage())

    def resolve(self, ref):
        result = super().resolve(ref)

        return result


class SchemaValidator:
    def __init__(self, openapi_filename: str):
        with open(openapi_filename) as file:
            openapi = yaml.load(file)
        self.openapi = openapi

    def create_validator(self, ref: str):
        resolver = ReferenceResolver('', self.openapi)
        schema = resolver.resolve(ref)

        draft_7_validator = Draft7Validator(schema[1], resolver=resolver)
        return draft_7_validator.validate
