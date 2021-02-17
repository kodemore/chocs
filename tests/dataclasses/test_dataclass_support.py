from dataclasses import dataclass, field
from typing import List

import pytest

from chocs.dataclasses import asdict, make_dataclass


def test_can_make_simple_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[str]

    # when
    pet = make_dataclass({"name": "Bobek", "age": 4, "tags": ["1", "a", "True"]}, Pet)

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
    pet = make_dataclass({"name": "Bobek", "age": 4, "tags": [{"name": "Cat"}, {"name": "Brown"}]}, Pet)

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
    pet = make_dataclass(json, Pet)

    # when
    data = asdict(pet)

    # then
    assert data == {
        "name": "Bobek",
        "age": 4,
        "tags": [
            {"name": "Cat"},
            {"name": "Brown"},
        ]
    }


def test_fail_make_with_missing_property() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int

    # when
    with pytest.raises(AttributeError) as error:
        make_dataclass({"name": "Bobek"}, Pet)

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
    pet = make_dataclass({"name": "Bobek"}, Pet)

    # then
    assert pet.name == "Bobek"
    assert pet.age == 10
    assert isinstance(pet.tags, list)
