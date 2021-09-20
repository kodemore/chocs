from chocs.rest import query


def test_can_create_equal_expression() -> None:
    # when
    expression = query.create_expression("test", "value")

    # then
    assert isinstance(expression, query.EqualExpression)
    assert expression.field == "test"
    assert expression.value == "value"

    # when
    expression = query.create_expression("test", "..")

    # then
    assert isinstance(expression, query.EqualExpression)
    assert expression.value == ".."


def test_can_create_greater_than_expression() -> None:
    # when
    expression = query.create_expression("test", ">3")

    # then
    assert isinstance(expression, query.GreaterThanExpression)
    assert expression.value == 3


def test_can_create_lower_than_expression() -> None:
    # when
    expression = query.create_expression("test", "<abba")

    # then
    assert isinstance(expression, query.LowerThanExpression)
    assert expression.value == "abba"


def test_can_create_pattern_expression() -> None:
    # when
    expression = query.create_expression("test", "*abba")

    # then
    assert isinstance(expression, query.PatternExpression)
    assert expression.end == "abba"
    assert expression.start == ""

    # when
    expression = query.create_expression("test", "abba*")

    # then
    assert isinstance(expression, query.PatternExpression)
    assert expression.start == "abba"
    assert expression.end == ""

    # when
    expression = query.create_expression("test", "ab*ba")

    # then
    assert isinstance(expression, query.PatternExpression)
    assert expression.start == "ab"
    assert expression.end == "ba"


def test_can_create_range_expression() -> None:
    # when
    expression = query.create_expression("test", "1..10")

    # then
    assert isinstance(expression, query.RangeExpression)
    assert expression.start == 1
    assert expression.end == 10

    # when
    expression = query.create_expression("test", "1970-10-12..2010-11-11")

    # then
    assert isinstance(expression, query.RangeExpression)
    assert expression.start == "1970-10-12"
    assert expression.end == "2010-11-11"

    # when
    expression = query.create_expression("test", "..10")

    # then
    assert isinstance(expression, query.RangeExpression)
    assert expression.start is None
    assert expression.end == 10

    # when
    expression = query.create_expression("test", "1.14..")

    # then
    assert isinstance(expression, query.RangeExpression)
    assert expression.start == 1.14
    assert expression.end is None
