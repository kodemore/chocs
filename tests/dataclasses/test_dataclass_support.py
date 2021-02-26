from dataclasses import dataclass, field

import pytest
from typing import Generic, List, TypeVar

from chocs.dataclasses import asdict, init_dataclass


def test_can_make_simple_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[str]

    # when
    pet = init_dataclass({"name": "Bobek", "age": 4, "tags": ["1", "a", "True"]}, Pet)

    # then
    assert isinstance(pet, Pet)
    assert pet.name == "Bobek"
    assert pet.age == 4
    assert len(pet.tags) == 3
    for tag in pet.tags:
        assert isinstance(tag, str)


def test_can_make_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    # when
    pet = init_dataclass(
        {"name": "Bobek", "age": 4, "tags": [{"name": "Cat"}, {"name": "Brown"}]}, Pet
    )

    # then
    assert isinstance(pet, Pet)
    assert pet.name == "Bobek"
    assert pet.age == 4
    assert len(pet.tags) == 2
    assert isinstance(pet.tags[0], Tag)
    assert pet.tags[0].name == "Cat"
    assert pet.tags[1].name == "Brown"


def test_can_extract_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    json = {"name": "Bobek", "age": 4, "tags": [{"name": "Cat"}, {"name": "Brown"}]}
    pet = init_dataclass(json, Pet)

    # when
    data = asdict(pet)

    # then
    assert data == {
        "name": "Bobek",
        "age": 4,
        "tags": [{"name": "Cat"}, {"name": "Brown"},],
    }


def test_fail_make_with_missing_property() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int

    # when
    with pytest.raises(AttributeError) as error:
        init_dataclass({"name": "Bobek"}, Pet)

    # then
    assert str(error.value) == "Property `age` is required."


def test_make_with_default_values() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int = 10
        tags: list = field(default_factory=list)

    # when
    pet = init_dataclass({"name": "Bobek"}, Pet)

    # then
    assert pet.name == "Bobek"
    assert pet.age == 10
    assert isinstance(pet.tags, list)


def _test_can_make_nested_dataclasses_from_generic_parent() -> None:
    T = TypeVar("T")

    @dataclass
    class Item:
        id: int

    @dataclass
    class Parent(Generic[T]):
        items: List[T]

    @dataclass
    class Child(Parent[Item]):
        name: str

    # when
    example = init_dataclass(
        {"name": "Example One", "items": [{"id": 1,}, {"id": 2,},]}, Child
    )

    # then
    assert isinstance(example, Child)
    assert example.name == "Example One"
    assert len(example.items) == 2
    item1 = example.items[0]
    item2 = example.items[1]
    assert isinstance(item1, Item)
    assert item1.id == 1
    assert isinstance(item2, Item)
    assert item2.id == 2


def _test_init_dataclass_supports_init_false_fields() -> None:
    @dataclass
    class Collection:
        items: List[int]
        total: int = field(init=False)

        def __post_init__(self):
            self.total = len(self.items)

    # when
    collection = init_dataclass(
        {"items": [1, 2, 3]},
        Collection
    )

    # then
    assert isinstance(collection, Collection)
    assert len(collection.items) == 3
    assert collection.total == 3
