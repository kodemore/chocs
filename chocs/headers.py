from typing import ItemsView
from typing import KeysView
from typing import Optional
from typing import ValuesView


def _normalize_header_name(name: str) -> str:
    """
    According to rfc https://www.ietf.org/rfc/rfc2616.txt header names are case insensitive,
    thus they can be normalized to ease usage of Headers class.
    :param name:
    :return:
    """
    name = name.lower()
    if name.startswith("http_"):
        name = name[5:]

    return name.replace("_", "-")


def _normalize_headers(headers: dict) -> dict:
    normalized = {}
    for name, value in headers.items():
        normalized[_normalize_header_name(name)] = value

    return normalized


class Headers:
    def __init__(self, headers: Optional[dict] = None):
        headers = {} if headers is None else headers
        assert isinstance(
            headers, dict
        ), "Failed to assert that headers are instance of dict"
        self._headers = _normalize_headers(headers)

    def add_header(self, name: str, value: str) -> None:
        self._headers[_normalize_header_name(name)] = value

    def get(self, name: str, default: str = "") -> str:
        if name in self:
            return self.__getitem__(name)
        return default

    def __getitem__(self, name: str) -> str:
        return self._headers[_normalize_header_name(name)]

    def __contains__(self, name: str) -> bool:
        return _normalize_header_name(name) in self._headers

    def items(self) -> ItemsView:
        return self._headers.items()

    def values(self) -> ValuesView:
        return self._headers.values()

    def keys(self) -> KeysView:
        return self._headers.keys()


__all__ = ["Headers"]
