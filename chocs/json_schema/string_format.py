from typing import Callable

from chocs.json_schema.format_validators import validate_format_boolean
from chocs.json_schema.format_validators import validate_format_bytes
from chocs.json_schema.format_validators import validate_format_date
from chocs.json_schema.format_validators import validate_format_datetime
from chocs.json_schema.format_validators import validate_format_decimal
from chocs.json_schema.format_validators import validate_format_email
from chocs.json_schema.format_validators import validate_format_hostname
from chocs.json_schema.format_validators import validate_format_ip_address
from chocs.json_schema.format_validators import validate_format_ip_address_v4
from chocs.json_schema.format_validators import validate_format_ip_address_v6
from chocs.json_schema.format_validators import validate_format_pattern
from chocs.json_schema.format_validators import validate_format_semver
from chocs.json_schema.format_validators import validate_format_time
from chocs.json_schema.format_validators import validate_format_time_duration
from chocs.json_schema.format_validators import validate_format_uri
from chocs.json_schema.format_validators import validate_format_url
from chocs.json_schema.format_validators import validate_format_uuid


class _StringFormat:
    BOOLEAN = "boolean"
    BYTE = "byte"
    DATE = "date"
    DATE_TIME = "date-time"
    DECIMAL = "decimal"
    EMAIL = "email"
    HOSTNAME = "hostname"
    IP_ADDRESS = "ip-address"
    IP_ADDRESS_V4 = "ip-address-v4"
    IP_ADDRESS_V6 = "ip-address-v6"
    PATTERN = "pattern"
    SEMVER = "semver"
    TIME = "time"
    TIME_DURATION = "time-duration"
    URI = "uri"
    URL = "url"
    UUID = "uuid"

    def __init__(self):
        self._formats = {
            self.BOOLEAN: validate_format_boolean,
            self.BYTE: validate_format_bytes,
            self.DATE: validate_format_date,
            self.DATE_TIME: validate_format_datetime,
            self.DECIMAL: validate_format_decimal,
            self.EMAIL: validate_format_email,
            self.HOSTNAME: validate_format_hostname,
            self.IP_ADDRESS: validate_format_ip_address,
            self.IP_ADDRESS_V4: validate_format_ip_address_v4,
            self.IP_ADDRESS_V6: validate_format_ip_address_v6,
            self.PATTERN: validate_format_pattern,
            self.SEMVER: validate_format_semver,
            self.TIME: validate_format_time,
            self.TIME_DURATION: validate_format_time_duration,
            self.URI: validate_format_uri,
            self.URL: validate_format_url,
            self.UUID: validate_format_uuid,
        }

    def __getitem__(self, format_name: str) -> Callable:
        if format_name in self._formats:
            return self._formats[format_name]
        raise KeyError(f"Unsupported format {format_name}")

    def __setitem__(self, format_name: str, value: Callable) -> None:
        self._formats[format_name] = value

    def __contains__(self, format_name: str) -> bool:
        return format_name in self._formats


StringFormat = _StringFormat()


__all__ = ["StringFormat"]
