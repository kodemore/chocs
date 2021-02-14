import datetime
import ipaddress
import uuid
from decimal import Decimal
from functools import partial
from inspect import isclass
from typing import Any, AnyStr, ByteString, Callable, Dict, List, Pattern, Protocol, Set, Type, Union, Sequence, Tuple
from dataclasses import is_dataclass, MISSING, _MISSING_TYPE
from enum import Enum
from abc import ABC, abstractmethod


class Hydrator(ABC):
    @abstractmethod
    def hydrate(self, value: Any) -> Any:
        ...

    @abstractmethod
    def extract(self, value: Any) -> Any:
        ...


class DataclassHydrator(Hydrator):
    def __init__(self, dataclass_name: Type):
        self.hydrators = {}
        self.setters = {}
        self.dataclass_name = dataclass_name

        fields = dataclass_name.__dataclass_fields__

        for field_name, field_descriptor in fields.items():
            self.hydrators[field_name] = build_hydrator_for_type(field_descriptor.type)

            # Sadly setting value is a bit more complex than getting it in dataclasses
            self.setters[field_name] = partial(
                set_dataclass_property,
                hydrator=self.hydrators[field_name],
                property_name=field_name,
                default_factory=field_descriptor.default_factory,
                default_value=field_descriptor.default
            )

    def hydrate(self, value: Any) -> Any:
        instance = self.dataclass_name.__new__(self.dataclass_name)

        for name, setter in self.setters.items():
            setter(instance, value)

        return instance

    def extract(self, value: Any) -> Any:
        result = {}
        for name, hydrator in self.hydrators.items():
            result[name] = hydrator.extract(getattr(value, name, None))

        return result


class AnyHydrator(Hydrator):
    def hydrate(self, value: Any, *args) -> Any:
        return value

    def extract(self, value: Any, *args) -> Any:
        return value


class SimpleHydrator(Hydrator):
    def __init__(self, primitive_type: Type):
        self.primitive_type = primitive_type

    def hydrate(self, value: Any, *args) -> Any:
        if isinstance(value, self.primitive_type):
            return value

        raise ValueError(f"Unexpected value `{value}` expected `{self.primitive_type}`.")

    def extract(self, value: Any, *args) -> Any:
        return value


class ListHydrator(Hydrator):
    def __init__(self, subtype_hydrator: Hydrator):
        self.subtype_hydrator = subtype_hydrator[0]

    def hydrate(self, value: Any) -> Any:
        return [self.subtype_hydrator.hydrate(item) for item in value]

    def extract(self, value: Any) -> Any:
        return [self.subtype_hydrator.extract(item) for item in value]


class EnumHydrator(Hydrator):
    def __init__(self, enum_class: Type[Enum]):
        self.enum_class = enum_class

    def hydrate(self, value: Any) -> Any:
        return self.enum_class(value)

    def extract(self, value: Any) -> Any:
        return value.value


class UnionHydrator(Hydrator):
    def hydrate(self, value: Any, *args) -> Any:
        return value

    def extract(self, value: Any, *args) -> Any:
        return value


class DecimalHydrator(Hydrator):
    def hydrate(self, value: Any, *args) -> Any:
        if isinstance(value, Decimal):
            return value

        return Decimal(value)

    def extract(self, value: Any, *args) -> Any:
        return str(value)


TYPE_HYDRATORS = {
    bool: SimpleHydrator(bool),
    int: SimpleHydrator(int),
    float: SimpleHydrator(float),
    str: SimpleHydrator(str),
    bytes: SimpleHydrator(bytes),
    list: SimpleHydrator(list),
    set: SimpleHydrator(set),
    tuple: SimpleHydrator(tuple),
    dict: SimpleHydrator(dict),
    List: SimpleHydrator(list),
    Sequence: SimpleHydrator(list),
    Tuple: SimpleHydrator(tuple),
    Set: SimpleHydrator(set),
    Decimal: DecimalHydrator(),
    Any: AnyHydrator(),
    AnyStr: SimpleHydrator(str),
}

DATACLASS_HYDRATORS = {}


def set_dataclass_property(
    obj: object,
    attributes: Dict[str, Any],
    property_name: str,
    hydrator: Hydrator,
    default_factory: Union[Callable, _MISSING_TYPE],
    default_value: Any
) -> None:
    if property_name in attributes:
        setattr(obj, property_name, hydrator.hydrate(attributes[property_name]))
        return

    if default_factory is not MISSING:
        setattr(obj, property_name, default_factory())
        return

    if default_value is not MISSING:
        setattr(obj, property_name, default_value)
        return

    attribute_value = attributes.get(property_name, MISSING)
    try:
        setattr(hydrator.hydrate(attribute_value))
    except ValueError as error:
        if attribute_value is MISSING:
            raise AttributeError(f"Property `{property_name}` is required.") from error
        raise error


def build_hydrator_for_type(type_name: Type) -> Hydrator:
    if is_dataclass(type_name):
        if type_name not in DATACLASS_HYDRATORS:
            DATACLASS_HYDRATORS[type_name] = DataclassHydrator(type_name)

        return DATACLASS_HYDRATORS[type_name]

    if type_name in TYPE_HYDRATORS:
        return TYPE_HYDRATORS[type_name]

    origin_type = getattr(type_name, "__origin__", None)

    if origin_type is None:
        if not isclass(type_name):
            return TYPE_HYDRATORS[Any]

        if issubclass(type_name, Enum):
            return EnumHydrator(type_name)

        return TYPE_HYDRATORS[Any]

    if origin_type not in TYPE_HYDRATORS:
        return TYPE_HYDRATORS[Any]

    subtypes = []
    for subtype in type_name.__args__:
        if subtype is ...:
            subtypes.append(...)
            continue
        subtypes.append(build_hydrator_for_type(subtype))

    if origin_type is list:
        return ListHydrator(subtypes)

    return TYPE_HYDRATORS[Any]



