from functools import partial
from json import load as load_json
from os import path
from typing import Any, Dict, Optional
from yaml import FullLoader as YamlFullLoader, load as load_yaml

load_yaml = partial(load_yaml, Loader=YamlFullLoader)


class URILoader:
    LOADERS = {
        "yaml": load_yaml,
        "yml": load_yaml,
        "json": load_json,
    }

    def __init__(self):
        self.store = {}

    def load(self, uri: str) -> dict:
        if uri not in self.store:
            contents = JsonReferenceResolver.resolve(self._load_file_contents(uri), uri)
            self.store[uri] = contents

        return self.store[uri]

    def _load_file_contents(self, file_name: str) -> dict:
        file_name = path.abspath(file_name)
        file = open(file_name)
        extension = file_name.split(".")[-1]
        if extension not in URILoader.LOADERS:
            raise TypeError(f"Could not resolve uri `{file_name}`")

        return self.LOADERS[extension](file)  # type: ignore


_default_uri_loader = URILoader()


class JsonReference:
    def __init__(self, uri: str, loader: URILoader = _default_uri_loader):
        self.uri, self.reference = uri.split("#")
        self.id = uri
        self._loader = loader
        self._data: Optional[Dict] = None

    def __contains__(self, item) -> bool:
        return item in self.data

    def __getitem__(self, key: str):
        return self.data[key]

    @property
    def data(self) -> dict:
        if self._data:
            return self._data

        schema = self._loader.load(self.uri)
        reference_path = self.reference.lstrip("#").strip("/").split("/")
        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {self.reference}")
            schema = schema[item]

        if isinstance(schema, JsonReference):
            self._data = schema.data

        self._data = schema  # type: ignore

        return self._data

    def __repr__(self) -> str:
        return f"JsonReference({self.id})"

    def __iter__(self):
        return iter(self.data)


class JsonReferenceResolver:
    """
    Replaces $ref objects inside schema with instances of JsonReference class.
    Given the following json dict passed as `obj` parameter:
    ```
    {"a": 1, "b": {"$ref": "#/a"}}
    ```
    the `{"$ref": "#/a"}` part will be replaced by JsonReference instance, containing `{"a": 1}` value.
    """

    reference_store: Dict[str, JsonReference] = {}

    @classmethod
    def resolve(cls, obj: Any, base_uri: str = ""):
        try:
            if not isinstance(obj["$ref"], str):
                raise TypeError
            return cls._create_reference(obj, base_uri)
        except (TypeError, LookupError):
            pass

        if isinstance(obj, list):
            return [cls.resolve(item, base_uri) for item in obj]

        elif isinstance(obj, dict):
            return {key: cls.resolve(value, base_uri) for key, value in obj.items()}

        return obj

    @classmethod
    def _create_reference(cls, ref_obj: dict, base_uri: str) -> JsonReference:
        ref_str = ref_obj["$ref"]
        uri_part, ref_part = ref_str.split("#")
        if not uri_part:
            uri = base_uri
        else:
            uri = path.join(path.dirname(base_uri), uri_part)

        full_ref = uri + "#" + ref_part

        if full_ref not in cls.reference_store:
            cls.reference_store[full_ref] = JsonReference(full_ref)

        return cls.reference_store[full_ref]


class OpenApiSchema:
    def __init__(self, file_name: str, loader: URILoader = _default_uri_loader):
        self.file_name = file_name
        self._contents: Optional[dict] = None
        self.loader = loader

    @property
    def contents(self) -> dict:
        if self._contents is None:
            self._contents = self.loader.load(self.file_name)

        return self._contents

    def query(self, reference: str) -> Any:
        reference = reference.replace("\\/", "&slash;")
        reference_path = [part.replace("&slash;", "/") for part in reference.lstrip("#").strip("/").split("/")]
        schema = self.contents

        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {reference}")
            schema = schema[item]

        return schema

    def __getitem__(self, item: str) -> Any:
        return self.contents[item]

    def __contains__(self, item: str) -> bool:
        return item in self.contents

    def __iter__(self):
        return iter(self.contents)


__all__ = ["JsonReference", "JsonReferenceResolver", "OpenApiSchema", "URILoader"]
