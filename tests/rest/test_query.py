from chocs.rest.query import Query, PatternExpression, GreaterThanExpression
from chocs.http.http_query_string import HttpQueryString


def test_can_instantiate() -> None:
    # when
    query = Query(HttpQueryString("limit=10&name=Bob*&age=>10"), ["name", "age"])

    # then
    assert isinstance(query, Query)

    assert "name" in query.fields
    assert isinstance(query.fields["name"], PatternExpression)
    assert query.fields["name"].start == "Bob"

    assert "age" in query.fields
    assert isinstance(query.fields["age"], GreaterThanExpression)
    assert query.fields["age"].value == 10
