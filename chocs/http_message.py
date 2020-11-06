import json
from collections import UserDict
from io import BytesIO
from json.decoder import JSONDecodeError
from typing import Any
from typing import Optional

from .http_multipart_message_parser import parse_multipart_message
from .http_query_string import parse_qs


class HttpMessage(str):
    pass


class CompositeHttpMessage(UserDict, HttpMessage):
    def get(self, name: str, default: Optional[Any] = None) -> Any:
        if name in self:
            return self[name]

        return default


class FormHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, encoding: str = "utf8") -> "FormHttpMessage":
        body.seek(0)
        decoded_input = body.read().decode(encoding)
        fields = parse_qs(decoded_input)
        instance = FormHttpMessage()

        for name, value in fields.items():
            instance[name] = value

        return instance


class JsonHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, encoding: str = "utf8") -> "JsonHttpMessage":
        body.seek(0)
        decoded_input = body.read().decode(encoding)

        try:
            body = json.loads(decoded_input)
        except JSONDecodeError:
            body = {}

        instance = JsonHttpMessage(body)

        return instance


class MultipartHttpMessage(CompositeHttpMessage):
    @staticmethod
    def from_bytes(body: BytesIO, boundary: str, encoding: str = "utf8") -> "MultipartHttpMessage":
        body.seek(0)
        fields = parse_multipart_message(body.read(), boundary, encoding)

        instance = MultipartHttpMessage()

        for name, value in fields.items():
            instance[name] = value

        return instance


__all__ = ["HttpMessage", "CompositeHttpMessage", "FormHttpMessage", "JsonHttpMessage", "MultipartHttpMessage"]
