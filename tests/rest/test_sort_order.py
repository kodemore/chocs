from chocs.rest.query import create_sort_order, SortOrder, SortDirection


def test_can_create_sort_order() -> None:
    # when
    expression = create_sort_order("-name,+age , email", ["name", "age", "email"])

    # then
    assert isinstance(expression, SortOrder)
    assert "name" in expression
    assert "age" in expression
    assert "email" in expression

    assert expression["name"] == SortDirection.DESCENDING
    assert expression["age"] == SortDirection.ASCENDING
    assert expression["email"] == SortDirection.ASCENDING


def test_can_filter_fields_in_sort_order() -> None:
    # when
    expression = create_sort_order("-name,+age , email", ["name"])

    # then
    assert isinstance(expression, SortOrder)
    assert "name" in expression
    assert "age" not in expression
    assert "email" not in expression

    assert expression["name"] == SortDirection.DESCENDING
