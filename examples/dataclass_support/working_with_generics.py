from dataclasses import dataclass
from typing import Generic, List, TypeVar
from chocs.dataclasses import init_dataclass

T = TypeVar("T")


@dataclass
class Pet:
    name: str


@dataclass
class Animal:
    name: str


@dataclass
class CustomList(Generic[T]):
    list: List[T]


pet_list = init_dataclass(
    {
        "list": [
            {"name": "Boo"},
            {"name": "Bobek"},
        ]
    },
    CustomList[Pet],
)

assert isinstance(pet_list, CustomList)
for pet in pet_list.list:
    assert isinstance(pet, Pet)


animal_list = init_dataclass(
    {
        "list": [
            {"name": "Boo"},
            {"name": "Bobek"},
        ]
    },
    CustomList[Animal],
)

assert isinstance(pet_list, CustomList)
for animal in animal_list.list:
    assert isinstance(animal, Animal)
