from datetime import datetime
from http.cookies import SimpleCookie
from typing import List
from typing import Optional


class Cookie:
    def __init__(
        self,
        name: str,
        value: str,
        path: Optional[str] = None,
        domain: Optional[str] = None,
        expires: Optional[datetime] = None,
    ):
        self.name = name
        self.value = value
        self.path = path
        self.domain = domain
        self.expires = expires

        cookie: SimpleCookie = SimpleCookie()
        cookie[name] = str(value)
        if domain:
            cookie[name]["domain"] = domain
        if path:
            cookie[name]["path"] = path
        if expires:
            cookie[name]["expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.cookie = cookie

    def __str__(self) -> str:
        return str(self.cookie)

    def header(self) -> List[str]:
        return [part.strip() for part in str(self).split(":", 1)]


class CookieParser:
    def __init__(self, header: str):
        """
        When the user agent generates an HTTP request, the user agent MUST
        NOT attach more than one Cookie header field.
        https://tools.ietf.org/html/rfc6265#section-5.4

        Therefore CookieParser will only accept a single header string
        """
        self.header = header

    def to_list(self) -> List[Cookie]:
        simple_cookie: SimpleCookie = SimpleCookie()
        simple_cookie.load(self.header)
        return [
            Cookie(morsel.key, morsel.value) for key, morsel in simple_cookie.items()
        ]


__all__ = ["Cookie", "CookieParser"]
