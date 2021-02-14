from dataclasses import dataclass, field
from typing import List

import pytest

from chocs.dataclasses.hydrators import build_hydrator_for_type


def test_can_hydrate_simple_dataclass() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[str]
    hydrator = build_hydrator_for_type(Pet)

    # when
    pet = hydrator.hydrate({"name": "Bobek", "age": 4, "tags": ["1", "a", "True"]})

    # then
    assert isinstance(pet, Pet)
    assert pet.name == "Bobek"
    assert pet.age == 4
    assert len(pet.tags) == 3
    for tag in pet.tags:
        assert isinstance(tag, str)


def test_can_hydrate_nested_dataclasses() -> None:
    # given
    @dataclass
    class Tag:
        name: str

    @dataclass
    class Pet:
        name: str
        age: int
        tags: List[Tag]

    hydrator = build_hydrator_for_type(Pet)

    # when
    pet = hydrator.hydrate({"name": "Bobek", "age": "4", "tags": [{"name": "Cat"}, {"name": "Brown"}]})

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

    json = {"name": "Bobek", "age": "4", "tags": [{"name": "Cat"}, {"name": "Brown"}]}
    hydrator = build_hydrator_for_type(Pet)
    pet = hydrator.hydrate(json)

    # when
    data = hydrator.extract(pet)

    # then
    assert data == {
        "name": "Bobek",
        "age": 4,
        "tags": [
            {"name": "Cat"},
            {"name": "Brown"},
        ]
    }


def test_fail_hydrating_with_missing_property() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int
    hydrator = build_hydrator_for_type(Pet)

    # when
    with pytest.raises(AttributeError) as error:
        hydrator.hydrate({"name": "Bobek"})

    # then
    assert str(error.value) == "Property `age` is required."


def test_hydrate_with_default_values() -> None:
    # given
    @dataclass
    class Pet:
        name: str
        age: int = 10
        tags: list = field(default_factory=list)

    hydrator = build_hydrator_for_type(Pet)

    # when
    pet = hydrator.hydrate({"name": "Bobek"})

    # then
    assert pet.name == "Bobek"
    assert pet.age == 10
    assert isinstance(pet.tags, list)
