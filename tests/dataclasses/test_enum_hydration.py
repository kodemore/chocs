from enum import Enum, IntEnum
import pytest

from chocs.dataclasses.hydrators import build_hydrator_for_type


def test_hydrate_enum() -> None:
    # given
    class Colors(Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"
        ORANGE = "orange"

    hydrator = build_hydrator_for_type(Colors)

    # when
    hydrated_red = hydrator.hydrate("red")
    hydrated_orange = hydrator.hydrate("orange")

    # then
    assert isinstance(hydrated_red, Colors)
    assert hydrated_red == Colors.RED
    assert isinstance(hydrated_orange, Colors)
    assert hydrated_orange == Colors.ORANGE


def test_hydrate_int_enum() -> None:
    # given
    class Colors(IntEnum):
        RED = 1
        YELLOW = 2
        GREEN = 3
        ORANGE = 4
    hydrator = build_hydrator_for_type(Colors)

    # when
    hydrated_red = hydrator.hydrate(1)
    hydrated_orange = hydrator.hydrate(4)

    # then
    assert isinstance(hydrated_red, Colors)
    assert hydrated_red == Colors.RED
    assert isinstance(hydrated_orange, Colors)
    assert hydrated_orange == Colors.ORANGE


def test_extract_enum() -> None:
    # given
    class Colors(Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"
        ORANGE = "orange"
    hydrator = build_hydrator_for_type(Colors)
    hydrated_red = hydrator.hydrate("red")
    hydrated_orange = hydrator.hydrate("orange")

    # when
    extracted_red = hydrator.extract(hydrated_red)
    extracted_orange = hydrator.extract(hydrated_orange)

    # then
    assert extracted_red == "red"
    assert extracted_orange == "orange"


def test_fail_hydrating_invalid_enum() -> None:
    # given
    class Colors(Enum):
        RED = "red"
        YELLOW = "yellow"
        GREEN = "green"
        ORANGE = "orange"

    hydrator = build_hydrator_for_type(Colors)

    # when
    with pytest.raises(ValueError) as error:
        hydrator.hydrate("silver")

    # then
    assert str(error.value) == "'silver' is not a valid Colors"
