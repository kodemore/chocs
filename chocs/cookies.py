from datetime import datetime
from http.cookies import SimpleCookie
from typing import Optional, List


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
