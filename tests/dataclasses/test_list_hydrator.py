from chocs.dataclasses.hydrators import build_hydrator_for_type
from typing import List, Type, Sequence
import pytest


@pytest.mark.parametrize("list_type", [
    list,
    List,
    Sequence
])
def test_hydrate_generic_list(list_type: Type) -> None:
    # given
    list_hydrator = build_hydrator_for_type(list_type)
    list_items = ["a", 1, 2.1, True]

    # when
    mixed_list = list_hydrator.hydrate(list_items)

    # then
    assert mixed_list == list_items


def test_hydrate_typed_list() -> None:
    # given
    list_hydrator = build_hydrator_for_type(List[str])
    list_items = ["a", 1, 2.1, True]

    # when
    mixed_list = list_hydrator.hydrate(list_items)

    # then
    assert mixed_list == ["a", "1", "2.1", "True"]
