import pytest
import re
from base64 import b64encode
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID

from chocs.json_schema import StringFormat
from chocs.json_schema.errors import FormatValidationError
from chocs.json_schema.validators import validate_string_format


@pytest.mark.parametrize(
    "given_string, given_format, expected_value",
    [
        ["yes", StringFormat.BOOLEAN, True],
        ["ok", StringFormat.BOOLEAN, True],
        ["1", StringFormat.BOOLEAN, True],
        ["true", StringFormat.BOOLEAN, True],
        ["y", StringFormat.BOOLEAN, True],
        ["on", StringFormat.BOOLEAN, True],
        ["no", StringFormat.BOOLEAN, False],
        ["nope", StringFormat.BOOLEAN, False],
        ["off", StringFormat.BOOLEAN, False],
        ["false", StringFormat.BOOLEAN, False],
        ["0", StringFormat.BOOLEAN, False],
        [b64encode(b"format").decode("utf8"), StringFormat.BYTE, b"format"],
        ["20201220", StringFormat.DATE, date(year=2020, month=12, day=20)],
        [
            "20201220T121314",
            StringFormat.DATE_TIME,
            datetime(year=2020, month=12, day=20, hour=12, minute=13, second=14),
        ],
        ["12.1234", StringFormat.DECIMAL, Decimal("12.1234")],
        ["email@example.com", StringFormat.EMAIL, None],
        ["email@subdomain.example.com", StringFormat.EMAIL, None],
        ["firstname.lastname@example.com", StringFormat.EMAIL, None],
        ["firstname+lastname@example.com", StringFormat.EMAIL, None],
        ["email@123.123.123.123", StringFormat.EMAIL, None],
        ["1234567890@example.com", StringFormat.EMAIL, None],
        ["email@example-one.com", StringFormat.EMAIL, None],
        ["_______@example.com", StringFormat.EMAIL, None],
        ["email@example.name", StringFormat.EMAIL, None],
        ["email@example.museum", StringFormat.EMAIL, None],
        ["email@example.co.jp", StringFormat.EMAIL, None],
        ["firstname-lastname@example.com", StringFormat.EMAIL, None],
        ["google.com", StringFormat.HOSTNAME, None],
        ["test.foo.bar", StringFormat.HOSTNAME, None],
        ["localhost", StringFormat.HOSTNAME, None],
        ["0.0.0.0", StringFormat.IP_ADDRESS, IPv4Address("0.0.0.0")],
        ["127.0.0.1", StringFormat.IP_ADDRESS, IPv4Address("127.0.0.1")],
        [
            "1200:0000:AB00:1234:0000:2552:7777:1313",
            StringFormat.IP_ADDRESS,
            IPv6Address("1200:0000:AB00:1234:0000:2552:7777:1313"),
        ],
        [
            "21DA:D3:0:2F3B:2AA:FF:FE28:9C5A",
            StringFormat.IP_ADDRESS,
            IPv6Address("21DA:D3:0:2F3B:2AA:FF:FE28:9C5A"),
        ],
        ["0.0.0.0", StringFormat.IP_ADDRESS_V4, IPv4Address("0.0.0.0")],
        ["127.0.0.1", StringFormat.IP_ADDRESS_V4, IPv4Address("127.0.0.1")],
        [
            "1200:0000:AB00:1234:0000:2552:7777:1313",
            StringFormat.IP_ADDRESS_V6,
            IPv6Address("1200:0000:AB00:1234:0000:2552:7777:1313"),
        ],
        [
            "21DA:D3:0:2F3B:2AA:FF:FE28:9C5A",
            StringFormat.IP_ADDRESS_V6,
            IPv6Address("21DA:D3:0:2F3B:2AA:FF:FE28:9C5A"),
        ],
        ["0.", StringFormat.PATTERN, re.compile("0.")],
        ["[a-z]", StringFormat.PATTERN, re.compile("[a-z]")],
        ["1.0.0", StringFormat.SEMVER, None],
        ["1.0.0-alpha", StringFormat.SEMVER, None],
        ["1.0.0-alpha.1", StringFormat.SEMVER, None],
        ["1.0.0-0.3.7", StringFormat.SEMVER, None],
        ["1.0.0-x.7.z.92", StringFormat.SEMVER, None],
        ["12:15:18", StringFormat.TIME, time(hour=12, minute=15, second=18)],
        ["P1W", StringFormat.TIME_DURATION, timedelta(weeks=1)],
        ["PT1H", StringFormat.TIME_DURATION, timedelta(hours=1)],
        ["http://foo.com/blah_blah", StringFormat.URI, None],
        ["spotify://userid:password@example.com", StringFormat.URI, None],
        ["https://142.42.1.1:8080/", StringFormat.URI, None],
        ["slack://124435", StringFormat.URI, None],
        ["http://foo.com/blah_blah", StringFormat.URL, None],
        ["http://foo.com/blah_blah/", StringFormat.URL, None],
        ["https://www.example.com/foo/?bar=baz&inga=42&quux", StringFormat.URL, None],
        ["http://userid:password@example.com", StringFormat.URL, None],
        ["http://142.42.1.1:8080/", StringFormat.URL, None],
        ["http://142.42.1.1/", StringFormat.URL, None],
        ["http://code.google.com/events/#&product=browser", StringFormat.URL, None],
        ["http://a.b-c.de", StringFormat.URL, None],
        ["https://foo_bar.example.com/", StringFormat.URL, None],
        ["http://jabber.tcp.gmail.com", StringFormat.URL, None],
        ["http://_jabber._tcp.gmail.com", StringFormat.URL, None],
        ["http://مثال.إختبار", StringFormat.URL, None],
        [
            "cff801a5-5db7-4287-9414-64ba51a9a730",
            StringFormat.UUID,
            UUID("cff801a5-5db7-4287-9414-64ba51a9a730"),
        ],
        [
            "ad047288-b643-4cd0-8c79-354f68140bef",
            StringFormat.UUID,
            UUID("ad047288-b643-4cd0-8c79-354f68140bef"),
        ],
        [
            "b11b1836-ad3e-4944-9c80-eaccdac0487b",
            StringFormat.UUID,
            UUID("b11b1836-ad3e-4944-9c80-eaccdac0487b"),
        ],
        [
            "e643c4f2-f9c1-4287-b465-1e02ba7d902d",
            StringFormat.UUID,
            UUID("e643c4f2-f9c1-4287-b465-1e02ba7d902d"),
        ],
        [
            "57766d9b-9ea2-4740-9b26-56dfdd79678a",
            StringFormat.UUID,
            UUID("57766d9b-9ea2-4740-9b26-56dfdd79678a"),
        ],
    ],
)
def test_pass_valid_format(
    given_string: str, given_format: str, expected_value: Any
) -> None:
    if expected_value is None:
        expected_value = given_string
    assert validate_string_format(given_string, given_format) == expected_value


@pytest.mark.parametrize(
    "given_string, given_format",
    [
        ["invalid", StringFormat.BOOLEAN],
        ["invalid", StringFormat.BYTE],
        ["invalid", StringFormat.DATE],
        ["invalid", StringFormat.DATE_TIME],
        ["invalid", StringFormat.DECIMAL],
        ["invalid", StringFormat.EMAIL],
        ["__invalid", StringFormat.HOSTNAME],
        ["invalid", StringFormat.IP_ADDRESS],
        ["invalid", StringFormat.IP_ADDRESS_V4],
        ["invalid", StringFormat.IP_ADDRESS_V6],
        ["[0-$", StringFormat.PATTERN],
        ["invalid", StringFormat.SEMVER],
        ["invalid", StringFormat.TIME],
        ["invalid", StringFormat.TIME_DURATION],
        ["invalid", StringFormat.URI],
        ["invalid", StringFormat.URL],
        ["invalid", StringFormat.UUID],
    ],
)
def test_fail_invalid_format(given_string: str, given_format: str) -> None:
    with pytest.raises(FormatValidationError):
        validate_string_format(given_string, given_format)
