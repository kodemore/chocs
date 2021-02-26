from dataclasses import dataclass

import pytest
from typing import List, Sequence, Type, TypeVar, Generic
from dataclasses import dataclass

from chocs.dataclasses import get_strategy_for

T = TypeVar("T")


def test_hydrate_list_with_generic() -> None:
    # given
    @dataclass
    class Pet:
        name: str

    @dataclass
    class MyList(Generic[T]):
        count: int
        pets: List[T]

    strategy = get_strategy_for(MyList[Pet])
    raw_data = {"count": 2, "pets": [{"name": "Bobek"}, {"name": "Boo"}]}

    # when
    hydrated_data = strategy.hydrate(raw_data)

    # then
    assert isinstance(hydrated_data, MyList)
    for item in hydrated_data.pets:
        assert isinstance(item, Pet)
