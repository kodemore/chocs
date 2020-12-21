from functools import cached_property, partial
from json import load as json_load
from os import path
from typing import Dict, List, Optional, Union

from yaml import FullLoader as YamlFullLoader, load as yaml_load

yaml_load = partial(yaml_load, Loader=YamlFullLoader)


class URILoader:
    def __init__(self):
        self.store = {}

    def load(self, uri):
        if uri not in self.store:
            file_reader = FileReader(uri)
            self.store[uri] = file_reader.contents

        return self.store[uri]


_default_uri_loader = URILoader()


class JsonReference:
    def __init__(self, uri: str, loader: URILoader = _default_uri_loader):
        self.file_name, self.reference = uri.split("#")
        self.id = uri
        self._loader = loader

    def __getitem__(self, key: str):
        return self.data[key]

    @cached_property
    def data(self) -> dict:
        schema = self._loader.load(self.file_name)
        reference_path = self.reference.lstrip("#").strip("/").split("/")
        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {self.reference}")
            schema = schema[item]
        if isinstance(schema, JsonReference):
            return schema.data
        return schema

    def __repr__(self):
        return f"JsonReference({self.id})"


_default_store = {}


class FileReader:
    LOADERS = {
        "yaml": yaml_load,
        "yml": yaml_load,
        "json": json_load,
    }

    def __init__(self, file_name: str):
        self.extension = file_name.split(".")[-1]
        self.file_name = path.abspath(file_name)
        self._loader = FileReader.LOADERS[self.extension]
        self.store = _default_store

    def read(self) -> dict:
        file_handler = open(self.file_name)
        contents = self._loader(file_handler)
        file_handler.close()

        return self._replace_references(contents)

    def _replace_references(self, obj):
        try:
            if not isinstance(obj["$ref"], str):
                raise TypeError
            return self._create_reference(obj)
        except (TypeError, LookupError):
            pass

        if isinstance(obj, list):
            return [self._replace_references(item) for item in obj]

        elif isinstance(obj, dict):
            return {key: self._replace_references(value) for key, value in obj.items()}

        return obj

    def _create_reference(self, ref_obj: dict) -> JsonReference:
        ref_str = ref_obj["$ref"]
        file_part, ref_part = ref_str.split("#")
        if not file_part:
            file_part = self.file_name
        else:
            file_part = path.join(path.dirname(self.file_name), file_part)

        full_ref = file_part + "#" + ref_part

        if full_ref not in self.store:
            self.store[full_ref] = JsonReference(full_ref)

        return self.store[full_ref]

    @cached_property
    def contents(self) -> dict:
        return self.read()


class OpenApiSchema:
    def __init__(self, file_name: str, loader: URILoader = _default_uri_loader):
        self.file_name = file_name
        self.schema: dict = {}
        self.loader = loader

    @cached_property
    def contents(self) -> dict:
        return self.loader.load(self.file_name)

    def __getitem__(self, reference: str):
        reference_path = reference.lstrip("#").strip("/").split("/")
        schema = self.contents

        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {reference}")
            schema = schema[item]

        return schema
