from dataclasses import _process_class, MISSING
from typing import Any, Dict


def map_args_to_kwargs(kwargs, args, keys) -> Dict[str, Any]:
    all_kwargs = dict(kwargs)
    if args:
        for key, value in enumerate(args):
            all_kwargs[keys[key]] = value

    return all_kwargs


def _dataclass_init_override(self, *args, **kwargs) -> None:
    fields = self.__dataclass_fields__
    attributes = map_args_to_kwargs(kwargs, args, list(fields.keys()))

    for property_name, property_descriptor in fields.items():
        if property_name not in attributes:
            if property_descriptor.default_factory is not MISSING:
                setattr(self, property_name, property_descriptor.default_factory())
                continue

            if property_descriptor.default is not MISSING:
                setattr(self, property_name, property_descriptor.default)
                continue

            continue

        hydrator = HydratorResolver.resolve(property_descriptor.type)
        setattr(self, property_name, hydrator.hydrate(attributes[property_name]))


def dataclass(cls=None, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False):

    def wrap(cls):
        dataclass_class = _process_class(cls, init, repr, eq, order, unsafe_hash, frozen)
        dataclass_init = getattr(dataclass_class, "__init__")

        setattr(dataclass_class, "__init__", _dataclass_init_override)
        return dataclass_class

    if cls is None:
        return wrap

    return wrap(cls)
