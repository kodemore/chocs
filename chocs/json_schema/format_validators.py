import base64
import re
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from ipaddress import AddressValueError
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from typing import Any
from typing import Pattern
from typing import Union
from uuid import UUID

from .errors import FormatValidationError
from .iso_datetime import parse_iso_date_string
from .iso_datetime import parse_iso_datetime_string
from .iso_datetime import parse_iso_duration_string
from .iso_datetime import parse_iso_time_string


class StringFormats(Enum):
    EMAIL = "email"
    BYTE = "byte"
    PATTERN = "pattern"
    BOOLEAN = "boolean"
    DATE_TIME = "date-time"
    DATE = "date"
    TIME = "time"
    TIME_DURATION = "time-duration"
    HOSTNAME = "hostname"
    IP_ADDRESS = "ip-address"
    IP_ADDRESS_V4 = "ip-address-v4"
    IP_ADDRESS_V6 = "ip-address-v6"
    SEMVER = "semver"
    URI = "uri"
    URL = "url"
    UUID = "uuid"
    DECIMAL = "decimal"


def validate_format_pattern(value: Any) -> Pattern[str]:
    try:
        return re.compile(value)
    except Exception:
        raise FormatValidationError(expected_format=StringFormats.PATTERN)


def validate_format_bytes(value: Any) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)

    try:
        return base64.b64decode(value)
    except Exception:
        pass

    raise FormatValidationError(expected_format=StringFormats.BYTE)


FALSY_EXPRESSION = {0, "0", "no", "n", "nope", "false", "f", "off"}
TRUTHY_EXPRESSION = {1, "1", "ok", "yes", "y", "yup", "true", "t", "on"}


def validate_format_boolean(value: Any) -> bool:
    if value in FALSY_EXPRESSION:
        return False

    if value in TRUTHY_EXPRESSION:
        return True

    raise FormatValidationError(expected_format=StringFormats.BOOLEAN)


def validate_format_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value

    value = str(value)
    try:
        return parse_iso_datetime_string(value)
    except ValueError:
        raise FormatValidationError(expected_format=StringFormats.DATE_TIME)


def validate_format_date(value: Any) -> date:
    if isinstance(value, date):
        return value

    value = str(value)
    try:
        return parse_iso_date_string(value)
    except ValueError:
        raise FormatValidationError(expected_format=StringFormats.DATE)


def validate_format_time(value: Any) -> time:
    if isinstance(value, time):
        return value
    value = str(value)
    try:
        return parse_iso_time_string(value)
    except ValueError:
        raise FormatValidationError(expected_format=StringFormats.TIME)


def validate_format_time_duration(value: Any) -> timedelta:
    if isinstance(value, timedelta):
        return value

    value = str(value)
    try:
        return parse_iso_duration_string(value)
    except Exception:
        raise FormatValidationError(expected_format=StringFormats.TIME_DURATION)


# https://www.w3.org/TR/html5/forms.html#valid-e-mail-address
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    re.I,
)


def validate_format_email(value: str) -> str:
    """
    Keep in mind this validator willfully violates RFC 5322, the best way to invalidate email address is to send
    a message and receive confirmation from the recipient.
    """
    if not EMAIL_REGEX.match(value):
        raise FormatValidationError(expected_format=StringFormats.EMAIL)
    if ".." in value:
        raise FormatValidationError(expected_format=StringFormats.EMAIL)

    return value


HOSTNAME_REGEX = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[-0-9a-z]{0,61}[0-9a-z])?)*$", re.I,)


def validate_format_hostname(value: str) -> str:
    if not HOSTNAME_REGEX.match(value):
        raise FormatValidationError(expected_format=StringFormats.HOSTNAME)

    return value


def validate_format_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value

    try:
        value = Decimal(value)
        if not value.is_finite():
            raise FormatValidationError(expected_format=StringFormats.DECIMAL)

    except Exception:
        raise FormatValidationError(expected_format=StringFormats.DECIMAL)

    return value


def validate_format_ip_address_v4(value: Any) -> IPv4Address:
    try:
        return IPv4Address(value)
    except AddressValueError:
        raise FormatValidationError(expected_format=StringFormats.IP_ADDRESS_V4)


def validate_format_ip_address_v6(value: Any) -> IPv6Address:
    try:
        return IPv6Address(value)
    except AddressValueError:
        raise FormatValidationError(expected_format=StringFormats.IP_ADDRESS_V6)


def validate_format_ip_address(value: Any) -> Union[IPv4Address, IPv6Address]:
    try:
        return IPv4Address(value)
    except AddressValueError:
        try:
            return IPv6Address(value)
        except AddressValueError:
            raise FormatValidationError(expected_format=StringFormats.IP_ADDRESS)


SEMVER_REGEX = re.compile(
    r"^((([0-9]+)\.([0-9]+)\.([0-9]+)(?:-([0-9a-z-]+(?:\.[0-9a-z-]+)*))?)(?:\+([0-9a-z-]+(?:\.[0-9a-z-]+)*))?)$", re.I,
)


def validate_format_semver(value: Any) -> str:
    value = str(value)
    if not SEMVER_REGEX.match(value):
        raise FormatValidationError(expected_format=StringFormats.SEMVER)

    return value


URI_REGEX = re.compile(r"^(?:[a-z][a-z0-9+-.]*:)(?:\\/?\\/)?[^\s]*$", re.I)


def validate_format_uri(value: Any) -> str:
    value = str(value)
    if not URI_REGEX.match(value):
        raise FormatValidationError(expected_format=StringFormats.URI)

    return value


URL_REGEX = re.compile(
    r"^(?:(?:https?|ftp):\/\/)(?:\S+(?::\S*)?@)?(?:(?!10(?:\.\d{1,3}){3})(?!127(?:\.\d{1,3}){3})(?!169\.254(?:\.\d{1,3}){2})(?!192\.168(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9_]+-?)*[a-z\u00a1-\uffff0-9_]+)(?:\.(?:[a-z\u00a1-\uffff0-9_]+-?)*[a-z\u00a1-\uffff0-9_]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:\/[^\s]*)?$",
    re.I | re.U,
    )


def validate_format_url(value: Any) -> str:
    value = str(value)
    if not URL_REGEX.match(value):
        raise FormatValidationError(expected_format=StringFormats.URL)

    return value


def validate_format_uuid(value: Any) -> UUID:
    try:
        return UUID(value)
    except Exception:
        raise FormatValidationError(expected_format=StringFormats.UUID)

