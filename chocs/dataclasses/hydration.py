from abc import ABC, abstractmethod
from dataclasses import MISSING, _MISSING_TYPE, is_dataclass
from enum import Enum
from functools import partial
from inspect import isclass
from typing import Any, AnyStr, Callable, Dict, List, NamedTuple, Optional, Sequence, Set, Tuple, Type, TypeVar, Union

T = TypeVar("T")


class HydrationStrategy(ABC):
    @abstractmethod
    def hydrate(self, value: Any) -> Any:
        ...

    @abstractmethod
    def extract(self, value: Any) -> Any:
        ...


class DatalassStrategy(HydrationStrategy):
    def __init__(self, dataclass_name: Type):
        self._strategies = {}
        self._setters = {}
        self._dataclass_name = dataclass_name

        fields = dataclass_name.__dataclass_fields__

        for field_name, field_descriptor in fields.items():
            self._strategies[field_name] = get_strategy_for(field_descriptor.type)

            # Sadly setting value is a bit more complex than getting it in dataclasses
            self._setters[field_name] = partial(
                set_dataclass_property,
                strategy=self._strategies[field_name],
                property_name=field_name,
                default_factory=field_descriptor.default_factory,
                default_value=field_descriptor.default
            )

    def hydrate(self, value: Any) -> Any:
        instance = self._dataclass_name.__new__(self._dataclass_name)

        for name, setter in self._setters.items():
            setter(instance, value)

        return instance

    def extract(self, value: Any) -> Any:
        if not isinstance(value, self._dataclass_name):
            raise ValueError(f"Passed value must be type of {self._dataclass_name}.")

        result = {}
        for name, strategy in self._strategies.items():
            result[name] = strategy.extract(getattr(value, name, None))

        return result


class AnyStrategy(HydrationStrategy):
    def hydrate(self, value: Any, *args) -> Any:
        return value

    def extract(self, value: Any, *args) -> Any:
        return value


class SimpleStrategy(HydrationStrategy):
    def __init__(self, base_type: Type):
        self._base_type = base_type

    def hydrate(self, value: Any, *args) -> Any:
        return self._base_type(value)

    def extract(self, value: Any, *args) -> Any:
        return self._base_type(value)


class ListStrategy(HydrationStrategy):
    def __init__(self, subtype: HydrationStrategy):
        self._subtype = subtype

    def hydrate(self, value: Any) -> Any:
        return [self._subtype.hydrate(item) for item in value]

    def extract(self, value: Any) -> Any:
        return [self._subtype.extract(item) for item in value]


class TupleStrategy(HydrationStrategy):
    def __init__(self, subtypes: List[HydrationStrategy] = None):
        self._subtypes = subtypes
        self._subtypes_length = len(subtypes) if subtypes else 0
        self._is_ellipsis_present = self._subtypes[-1] is ... if subtypes else False
        self._is_dummy = self._subtypes_length == 0 or self._subtypes_length == 1 and self._is_ellipsis_present

    def hydrate(self, value: Any) -> Any:
        if self._is_dummy:
            return tuple(value)

        if self._is_ellipsis_present:
            return self._hydrate_ellipsis_tuple(value)

        result = []
        for index, subtype in enumerate(self._subtypes):
            result.append(subtype.hydrate(value[index]))

        return tuple(result)

    def extract(self, value: Any) -> Any:
        if self._is_dummy:
            return list(value)

        if self._is_ellipsis_present:
            return self._extract_ellipsis_tuple(value)

        return [subtype.extract(value[index]) for index, subtype in enumerate(self._subtypes)]

    def _hydrate_ellipsis_tuple(self, value) -> Any:
        last_known_strategy = self._subtypes[0]
        result = []
        for index, item in enumerate(value):
            if index + 1 < self._subtypes_length:
                last_known_strategy = self._subtypes[index]

            result.append(last_known_strategy.hydrate(item))

        return tuple(result)

    def _extract_ellipsis_tuple(self, value) -> Any:
        last_known_strategy = self._subtypes[0]
        result = []
        for index, item in enumerate(value):
            if index + 1 < self._subtypes_length:
                last_known_strategy = self._subtypes[index]

            result.append(last_known_strategy.extract(item))

        return result


class NamedTupleStrategy(HydrationStrategy):
    def __init__(self, class_name: Type[NamedTuple]):
        self._class_name = class_name
        self._is_typed = hasattr(class_name, "_field_types")
        self._arg_strategies: List[HydrationStrategy] = []
        if self._is_typed:
            self._build_type_mapper(class_name._field_types)

    def hydrate(self, value: Any) -> Any:
        if not self._is_typed:
            return self._class_name(*value)

        hydrated_values = []
        for index, item in enumerate(value):
            if index < len(self._arg_strategies):
                hydrated_values.append(self._arg_strategies[index].hydrate(item))
                continue
            hydrated_values.append(item)

        return self._class_name(*hydrated_values)

    def extract(self, value: Any) -> Any:
        result = list(value)
        if not self._is_typed:
            return result
        extracted_values = []
        for index, item in enumerate(result):
            if index < len(self._arg_strategies):
                extracted_values.append(self._arg_strategies[index].extract(item))
                continue
            extracted_values.append(item)

        return extracted_values

    def _build_type_mapper(self, field_types: Dict[str, Type]) -> None:
        for item_type in field_types.values():
            self._arg_strategies.append(get_strategy_for(item_type))


class EnumStrategy(HydrationStrategy):
    def __init__(self, class_name: Type[Enum]):
        self._class_name = class_name

    def hydrate(self, value: Any) -> Any:
        return self._class_name(value)

    def extract(self, value: Any) -> Any:
        return value.value


class UnionStrategy(HydrationStrategy):
    def hydrate(self, value: Any, *args) -> Any:
        return value

    def extract(self, value: Any, *args) -> Any:
        return value


def set_dataclass_property(
    obj: object,
    attributes: Dict[str, Any],
    property_name: str,
    strategy: HydrationStrategy,
    default_factory: Union[Callable, _MISSING_TYPE],
    default_value: Any
) -> None:
    if property_name in attributes:
        setattr(obj, property_name, strategy.hydrate(attributes[property_name]))
        return

    if default_factory is not MISSING:
        setattr(obj, property_name, default_factory())
        return

    if default_value is not MISSING:
        setattr(obj, property_name, default_value)
        return

    attribute_value = attributes.get(property_name, MISSING)

    if attribute_value is MISSING:
        raise AttributeError(f"Property `{property_name}` is required.")

    try:
        setattr(obj, property_name, strategy.hydrate(attribute_value))
    except Exception as error:
        raise AttributeError(f"Could not hydrate `{property_name}` property with `{attribute_value}` value.") from error


BUILT_IN_HYDRATOR_STRATEGY: Dict[Type, HydrationStrategy] = {
    bool: SimpleStrategy(bool),
    int: SimpleStrategy(int),
    float: SimpleStrategy(float),
    str: SimpleStrategy(str),
    bytes: SimpleStrategy(bytes),
    list: SimpleStrategy(list),
    set: SimpleStrategy(set),
    tuple: TupleStrategy(),
    dict: SimpleStrategy(dict),
    List: SimpleStrategy(list),
    Sequence: SimpleStrategy(list),
    Tuple: TupleStrategy(),
    Set: SimpleStrategy(set),
    Any: AnyStrategy(),
    AnyStr: SimpleStrategy(str),
}

CACHED_HYDRATION_STRATEGIES: Dict[Type, HydrationStrategy] = {}


def get_origin_type(type_name: Type) -> Optional[Type]:
    return getattr(type_name, '__origin__', None)


def get_type_args(type_name: Type) -> List[Type]:
    return getattr(type_name, '__args__', [])


def is_optional(type_name: Type) -> bool:
    return get_origin_type(type_name) is Union and get_type_args(type_name) and get_type_args(type_name)[-1] is type(None)


def unpack_optional(type_name: Type) -> Type:
    return get_type_args(type_name)[0]


def is_enum_type(type_name: Type) -> bool:
    return issubclass(type_name, Enum)


def is_named_tuple(type_name: Type) -> bool:
    return issubclass(type_name, tuple) and hasattr(type_name, "_fields")


def get_strategy_for(type_name: Type) -> HydrationStrategy:
    if type_name in BUILT_IN_HYDRATOR_STRATEGY:
        return BUILT_IN_HYDRATOR_STRATEGY[type_name]

    if type_name in CACHED_HYDRATION_STRATEGIES:
        return CACHED_HYDRATION_STRATEGIES[type_name]

    if is_dataclass(type_name):
        CACHED_HYDRATION_STRATEGIES[type_name] = DatalassStrategy(type_name)
        return CACHED_HYDRATION_STRATEGIES[type_name]

    origin_type = get_origin_type(type_name)

    if origin_type is None:
        if not isclass(type_name):
            return BUILT_IN_HYDRATOR_STRATEGY[Any]

        if is_enum_type(type_name):
            CACHED_HYDRATION_STRATEGIES[type_name] = EnumStrategy(type_name)
            return CACHED_HYDRATION_STRATEGIES[type_name]

        if is_named_tuple(type_name):
            CACHED_HYDRATION_STRATEGIES[type_name] = NamedTupleStrategy(type_name)
            return CACHED_HYDRATION_STRATEGIES[type_name]

        return BUILT_IN_HYDRATOR_STRATEGY[Any]

    if origin_type not in BUILT_IN_HYDRATOR_STRATEGY:
        return BUILT_IN_HYDRATOR_STRATEGY[Any]

    subtypes: List[HydrationStrategy] = []
    for subtype in get_type_args(type_name):
        if subtype is ...:
            subtypes.append(...)
            continue
        subtypes.append(get_strategy_for(subtype))

    if origin_type is list:
        CACHED_HYDRATION_STRATEGIES[type_name] = ListStrategy(subtypes[0])
        return CACHED_HYDRATION_STRATEGIES[type_name]

    if origin_type is tuple:
        CACHED_HYDRATION_STRATEGIES[type_name] = TupleStrategy(subtypes)
        return CACHED_HYDRATION_STRATEGIES[type_name]

    return BUILT_IN_HYDRATOR_STRATEGY[Any]
