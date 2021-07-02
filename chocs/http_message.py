import json
from abc import ABC
from copy import copy
from io import BytesIO
from json.decoder import JSONDecodeError
from typing import Any, Dict, ItemsView, KeysView, Optional, ValuesView

import yaml

from .http_multipart_message_parser import parse_multipart_message
from .http_query_string import parse_qs


class HttpMessage(ABC):
    pass


class SimpleHttpMessage(HttpMessage, str):
    def __new__(cls, value, *args, **kwargs):
        return super(SimpleHttpMessage, cls).__new__(cls, value)

    def __init__(self, value: str):
        # ignore value, as strings are immutable and this should be passed to __new__ constructor
        ...


class CompositeHttpMessage(HttpMessage):
    def __init__(self, data: Any) -> None:
        self.data = data

    def get(self, name: str, default: Optional[Any] = None) -> Any:
        if name in self:
            return self[name]

        return default

    def __getitem__(self, key) -> Any:
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __copy__(self):
        return type(self)(copy(self.data))

    def __iter__(self):
        return iter(self.data)

    def items(self) -> ItemsView:
        return self.data.items()

    def values(self) -> ValuesView:
        return self.data.values()

    def keys(self) -> KeysView:
        return self.data.keys()

    def __int__(self):
        return int(self.data)

    def __str__(self):
        return str(self.data)

    def __float__(self):
        return float(self.data)

    def __bool__(self):
        return bool(self.data)


class YamlHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, encoding: str = "utf8") -> "YamlHttpMessage":
        body.seek(0)
        decoded_input = body.read().decode(encoding)

        parsed_body: Dict[str, Any] = {}
        try:
            parsed_body = yaml.safe_load_all(decoded_input)  # type: ignore
        except JSONDecodeError:
            ...  # ignore

        return YamlHttpMessage(parsed_body)


class FormHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, encoding: str = "utf8") -> "FormHttpMessage":
        body.seek(0)
        decoded_input = body.read().decode(encoding)
        fields = parse_qs(decoded_input)
        return FormHttpMessage(fields)


class JsonHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, encoding: str = "utf8") -> "JsonHttpMessage":
        body.seek(0)
        decoded_input = body.read().decode(encoding)

        parsed_body: Dict[str, Any] = {}
        try:
            parsed_body = json.loads(decoded_input)
        except JSONDecodeError:
            ...  # ignore

        return JsonHttpMessage(parsed_body)


class MultipartHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, boundary: str, encoding: str = "utf8") -> "MultipartHttpMessage":
        body.seek(0)
        fields = parse_multipart_message(body.read(), boundary, encoding)

        return MultipartHttpMessage(fields)


__all__ = [
    "HttpMessage",
    "CompositeHttpMessage",
    "FormHttpMessage",
    "JsonHttpMessage",
    "MultipartHttpMessage",
    "SimpleHttpMessage",
    "YamlHttpMessage",
]
