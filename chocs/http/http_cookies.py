from __future__ import annotations

import re
from copy import copy
from datetime import datetime
from enum import Enum
from typing import Dict, ItemsView, KeysView, Optional, Union, ValuesView, overload
from urllib.parse import quote, unquote

COOKIE_NAME_VALIDATOR = re.compile(r"[a-z0-9!#$%&'*+.^_`|~\-]+", re.I)


class HttpCookieError(Exception):
    pass


class InvalidHttpCookieNameError(HttpCookieError, ValueError):
    pass


class InvalidHttpCookieValueError(HttpCookieError, ValueError):
    pass


class HttpCookieSameSitePolicy(Enum):
    STRICT = "Strict"
    LAX = "Lax"
    NONE = "None"


class HttpCookie:
    def __init__(
        self,
        name: str,
        value: str,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        expires: Optional[datetime] = None,
        max_age: Optional[int] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Union[bool, HttpCookieSameSitePolicy] = False,
    ):
        if not COOKIE_NAME_VALIDATOR.match(name):
            raise InvalidHttpCookieNameError(f"Invalid cookie name {name}, cookie name must be valid RFC 2616 token.")
        self._name: str = name
        self.value = value
        self.path = path
        self.domain = domain
        self.expires = expires
        self.max_age = max_age
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

    @property
    def name(self):
        """
        Cookie's name must be valid RFC-2616 token. Once set should not be changed as this causes some implications
        how we keep cookies in the cookie jar.
        .. _RFC-2616 token: https://tools.ietf.org/html/rfc2616#section-2.2
        """
        return self._name

    @property
    def safe_value(self) -> str:
        return quote(self.value)

    def __str__(self) -> str:
        return self.value

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    @overload  # type: ignore
    def __eq__(self, other: HttpCookie) -> bool:
        ...

    @overload
    def __eq__(self, other: str) -> bool:
        ...

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.value == other

        if not isinstance(other, HttpCookie):
            raise TypeError(
                f"HttpCookie.__eq__ expects either instance of `HttpCookie` or `str`," f" {type(other)} passed instead."
            )

        return (
            self.name == other.name
            and self.value == other.value
            and self.path == other.path
            and self.domain == other.domain
            and self.expires == other.expires
            and self.max_age == other.max_age
            and self.secure == other.secure
            and self.http_only == other.http_only
            and self.same_site == other.same_site
        )

    def serialise(self) -> str:
        output = f"{self.name}={self.safe_value}"
        if self.max_age is not None:
            output += f"; Max-Age={self.max_age}"

        if self.domain is not None:
            output += f"; Domain={self.domain}"

        if self.path is not None:
            output += f"; Path={self.path}"

        if self.expires is not None:
            output += f"; Expires={self.expires.strftime('%a, %d %b %Y %H:%M:%S %z')}"

        if self.secure:
            output += "; Secure"

        if self.http_only:
            output += "; HttpOnly"

        if self.same_site:
            if isinstance(self.same_site, HttpCookieSameSitePolicy):
                output += f"; SameSite={self.same_site.value}"
            else:
                output += "; SameSite=Strict"

        return output

    def __copy__(self) -> HttpCookie:
        new_copy = HttpCookie.__new__(HttpCookie)
        new_copy._name = self._name
        new_copy.value = self.value
        new_copy.path = self.path
        new_copy.domain = self.domain
        new_copy.expires = self.expires
        new_copy.max_age = self.max_age
        new_copy.secure = self.secure
        new_copy.http_only = self.http_only
        new_copy.same_site = self.same_site

        return new_copy


class HttpCookieJar:
    def __init__(self):
        self._cookies: Dict[str, HttpCookie] = {}

    def append(self, cookie: HttpCookie) -> None:
        self._cookies[cookie.name] = cookie

    def __setitem__(self, key: str, value: str) -> None:
        if isinstance(value, str):
            cookie = HttpCookie(key, value)
        else:
            raise InvalidHttpCookieValueError(
                "`HttpCookieJar.__setitem__` accepts only string values. "
                "To append new cookie use `HttpCookieJar.append` method instead."
            )
        self._cookies[key] = cookie

    def __getitem__(self, key: str) -> HttpCookie:
        return self._cookies[key]

    def __delitem__(self, key: str) -> None:
        del self._cookies[key]

    def __contains__(self, key: str) -> bool:
        return key in self._cookies

    def __len__(self) -> int:
        return len(self._cookies)

    def items(self) -> ItemsView[str, HttpCookie]:
        return self._cookies.items()

    def values(self) -> ValuesView[HttpCookie]:
        return self._cookies.values()

    def keys(self) -> KeysView[str]:
        return self._cookies.keys()

    def __repr__(self) -> str:
        return str(self._cookies)

    def __copy__(self) -> HttpCookieJar:
        new_copy = HttpCookieJar.__new__(HttpCookieJar)
        new_copy._cookies = {name: copy(value) for name, value in self.items()}

        return new_copy


def parse_cookie_header(header: str) -> HttpCookieJar:
    """
    When the user agent generates an HTTP request, the user agent MUST
    NOT attach more than one Cookie header field.
    https://tools.ietf.org/html/rfc6265#section-5.4
    Therefore parse_cookie_header will only accept a single header string
    """
    result = HttpCookieJar()

    cookies = header.split(";")
    for cookie in cookies:
        separator_position = cookie.find("=")
        if separator_position < 0:  # Broken cookie?
            continue
        try:
            result.append(
                HttpCookie(
                    cookie[0:separator_position].strip(),
                    unquote(cookie[separator_position + 1 :].strip()),
                )
            )
        except HttpCookieError:  # Invalid cookie name
            continue
    return result


__all__ = [
    "HttpCookie",
    "HttpCookieJar",
    "parse_cookie_header",
    "HttpCookieSameSitePolicy",
    "HttpCookieError",
]
