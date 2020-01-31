from pytest import mark
from pytest import raises

from chocs.query_string import build_dict_from_path
from chocs.query_string import parse_qs
from chocs.query_string import QueryString


@mark.parametrize(
    "query_string,expected",
    [["a", {"a": 1}], ["a[]", {"a": [1]}], ["a[a]", {"a": {"a": 1}}]],
)
def test_build_dict_from_path(query_string: str, expected: dict) -> None:
    assert build_dict_from_path(query_string, 1) == expected


@mark.parametrize("query_string", ["[a]", "[a[]]", "[a][a]", "[]"])
def test_if_fail_build_dict_from_path(query_string: str):
    with raises(ValueError):
        build_dict_from_path(query_string, 1)


def test_parse_qs_with_no_value():
    result = parse_qs("")
    assert isinstance(result, dict)
    assert result == {}


def test_parse_qs_with_single_value():
    result = parse_qs("simple_example=test_value")
    assert "simple_example" in result
    assert result["simple_example"] == "test_value"


def test_parse_qs_with_multiple_values():
    result = parse_qs("test_1=1&test_2=2&test_3=3")
    assert result == {"test_1": "1", "test_2": "2", "test_3": "3"}


def test_parse_qs_with_array_values():
    result = parse_qs("test_1[]=1&test_1[]=2&test_1[]=3")
    assert result == {"test_1": ["1", "2", "3"]}


def test_parse_qs_with_dict_values():
    result = parse_qs("test_1[a]=1&test_1[b]=2&test_1[c]=3")
    assert result == {"test_1": {"a": "1", "b": "2", "c": "3"}}


def test_parse_qs_with_nested_arrays():
    result = parse_qs("test_1[][]=1&test_1[][]=2&test_1[][]=3")
    assert result == {"test_1": [["1"], ["2"], ["3"]]}


def test_parse_qs_with_indexed_arrays():
    result = parse_qs("test_1[0][]=1&test_1[0][]=2&test_1[0][]=3")
    assert result == {"test_1": {"0": ["1", "2", "3"]}}


def test_parse_qs_with_broken_key():
    result = parse_qs("test_1[[a][b]]=1&test_1[b]=2&test_1[c]=3")
    assert result == {"test_1[[a][b]]": "1", "test_1": {"b": "2", "c": "3"}}


def test_query_string_instantiation():
    instance = QueryString("test_1[0][]=1&test_1[0][]=2&test_1[0][]=3")

    assert "test_1" in instance
    assert instance["test_1"] == {"0": ["1", "2", "3"]}


def test_query_string_with_repeated_key():
    result = parse_qs("test_1=1&test_1=2&test_1=3")
    assert result == {"test_1": ["1", "2", "3"]}


def test_query_string_with_repeated_key_and_arrays():
    result = parse_qs("test_1=1&test_1[]=2&test_1[]=3")
    assert result == {"test_1": ["1", "2", "3"]}


def test_query_string_with_repeated_key_and_dict():
    result = parse_qs("test_1=1&test_1[a]=2&test_1[b]=3")
    assert result == {"test_1": {"": "1", "a": "2", "b": "3"}}


@mark.parametrize(
    "query_string,expected",
    [["a=1", {"a": "1"}], ["a%5B%5D=1", {"a": ["1"]}], ["a%5Ba%5D=1", {"a": {"a": "1"}}]],
)
def test_quoted_query_string(query_string: str, expected: dict) -> None:
    assert parse_qs(query_string) == expected
