from chocs.http import HttpQueryString
from chocs.query import QueryCriteria, Expression


def test_can_instantiate() -> None:
    # when
    query = QueryCriteria(HttpQueryString("limit=10&name=Bob*&age=>10&tags=one,two,three&sort=-name,+age"))

    # then
    assert isinstance(query, QueryCriteria)

    assert "name" in query
    assert isinstance(query["name"], Expression)
    assert query["name"].start == "Bob"

    assert "age" in query
    assert isinstance(query["age"], Expression)
    assert query["age"].value == 10

    assert "tags" in query
    assert query["tags"]

    assert "limit" not in query


def test_can_generate_next_query_for_offset_based() -> None:
    # given
    query = QueryCriteria(HttpQueryString("limit=10&name=Bob*&age=>10"))

    # when
    next_query_string = query.next_query()

    # then
    assert next_query_string == "name=Bob*&age=>10&limit=10&offset=10"


def test_can_generate_prev_query_for_offset_based() -> None:
    # given
    query = QueryCriteria(HttpQueryString("limit=10&name=Bob*&age=>10&offset=20"))

    # when
    next_query_string = query.prev_query()

    # then
    assert next_query_string == "name=Bob*&age=>10&limit=10&offset=10"


def test_can_generate_prev_query_for_non_sufficient_offset() -> None:
    # given
    query = QueryCriteria(HttpQueryString("limit=10&name=Bob*&age=>10&offset=2"))

    # when
    next_query_string = query.prev_query()

    # then
    assert next_query_string == "name=Bob*&age=>10&limit=10&offset=0"


def test_can_convert_query_criteria_to_query_string() -> None:
    # given
    query_criteria = QueryCriteria(HttpQueryString("limit=10&name=Bob*&age=>10&tags=2..10&sort=-age"))

    # when
    result = str(query_criteria)

    # then
    assert result == "name=Bob*&age=>10&tags=2..10&-age&limit=10&offset=0"


def test_can_iterate_over_query_criteria() -> None:
    # given
    query = QueryCriteria(HttpQueryString("limit=10&name=Bob*&age=>10&tags=2"))
    fields = []
    values = []

    # then
    for field, expr in query:
        fields.append(field)
        values.append(expr)
        assert isinstance(expr, Expression)

    assert len(fields) == 3
    assert fields == list(query.keys())
    assert values == list(query.values())
