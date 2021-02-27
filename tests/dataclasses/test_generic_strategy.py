from dataclasses import dataclass
from typing import Generic, List, TypeVar, cast

from chocs.dataclasses import get_strategy_for

T = TypeVar("T")

@dataclass
class Pet:
    name: str

@dataclass
class MyList(Generic[T]):
    count: int
    pets: List[T]


def test_hydrate_generic_dataclass() -> None:
    # given
    strategy = get_strategy_for(MyList[Pet])
    raw_data = {"count": 2, "pets": [{"name": "Bobek"}, {"name": "Boo"}]}

    # when
    hydrated_data = strategy.hydrate(raw_data)

    # then
    assert isinstance(hydrated_data, MyList)
    for item in hydrated_data.pets:
        assert isinstance(item, Pet)


def test_hydrate_dataclass_extending_generic_dataclass() -> None:
    # given
    @dataclass
    class MySuperList(MyList, Generic[T]):
        ...

    strategy = get_strategy_for(MySuperList[Pet])
    raw_data = {"count": 2, "pets": [{"name": "Bobek"}, {"name": "Boo"}]}

    # when
    hydrated_data = strategy.hydrate(raw_data)

    # then
    assert isinstance(hydrated_data, MySuperList)
    for item in hydrated_data.pets:
        assert isinstance(item, Pet)


def test_hydrate_generic_as_dataclass_attribute() -> None:
    # given
    @dataclass
    class PetAggregator:
        pet_list: MyList[Pet]

    strategy = get_strategy_for(PetAggregator)
    raw_data = {"pet_list": {"count": 2, "pets": [{"name": "Bobek"}, {"name": "Boo"}]}}

    # when
    hydrated_data = strategy.hydrate(raw_data)

    # then
    assert isinstance(hydrated_data, PetAggregator)
    for item in hydrated_data.pet_list.pets:
        assert isinstance(item, Pet)


def test_extract_generic_dataclass() -> None:
    # given
    strategy = get_strategy_for(MyList[Pet])

    data = MyList[Pet](count=2, pets=[
        Pet("Bobek"),
        Pet("Boo")
    ])

    # when
    extracted_data = strategy.extract(data)

    assert extracted_data == {"count": 2, "pets": [{"name": "Bobek"}, {"name": "Boo"}]}
