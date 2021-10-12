from chocs.query import expression


def test_can_create_equal_expression() -> None:
    # when
    expr = expression.parse_expression("value")

    # then
    assert isinstance(expr, expression.EqualExpression)
    assert expr.value == "value"

    # when
    expr = expression.parse_expression("..")

    # then
    assert isinstance(expr, expression.EqualExpression)
    assert expr.value == ".."


def test_can_create_greater_than_expression() -> None:
    # when
    expr = expression.parse_expression(">3")

    # then
    assert isinstance(expr, expression.GreaterThanExpression)
    assert expr.value == 3


def test_can_create_lower_than_expression() -> None:
    # when
    expr = expression.parse_expression("<abba")

    # then
    assert isinstance(expr, expression.LowerThanExpression)
    assert expr.value == "abba"


def test_can_create_pattern_expression() -> None:
    # when
    expr = expression.parse_expression("*abba")

    # then
    assert isinstance(expr, expression.PatternExpression)
    assert expr.end == "abba"
    assert expr.start == ""

    # when
    expr = expression.parse_expression("abba*")

    # then
    assert isinstance(expr, expression.PatternExpression)
    assert expr.start == "abba"
    assert expr.end == ""

    # when
    expr = expression.parse_expression("ab*ba")

    # then
    assert isinstance(expr, expression.PatternExpression)
    assert expr.start == "ab"
    assert expr.end == "ba"


def test_can_create_range_expression() -> None:
    # when
    expr = expression.parse_expression("1..10")

    # then
    assert isinstance(expr, expression.RangeExpression)
    assert expr.start == 1
    assert expr.end == 10

    # when
    expr = expression.parse_expression("1970-10-12..2010-11-11")

    # then
    assert isinstance(expr, expression.RangeExpression)
    assert expr.start == "1970-10-12"
    assert expr.end == "2010-11-11"

    # when
    expr = expression.parse_expression("..10")

    # then
    assert isinstance(expr, expression.RangeExpression)
    assert expr.start is None
    assert expr.end == 10

    # when
    expr = expression.parse_expression("1.14..")

    # then
    assert isinstance(expr, expression.RangeExpression)
    assert expr.start == 1.14
    assert expr.end is None


def test_can_create_in_expression() -> None:
    # when
    expr = expression.parse_expression("1, 2,3, test 1 , 12.34")

    # then
    assert isinstance(expr, expression.InExpression)
    assert expr.values == [1, 2, 3, "test 1", 12.34]


def test_can_escape_expression() -> None:
    # when
    expr = expression.parse_expression("\"1, 2,3, test 1 , 12.34\"")

    # then
    assert isinstance(expr, expression.EqualExpression)
    assert expr.value == "1, 2,3, test 1 , 12.34"

    # when
    expr = expression.parse_expression("\"1..10\"")

    # then
    assert isinstance(expr, expression.EqualExpression)
    assert expr.value == "1..10"
