from functools import cached_property, partial
from json import load as json_load
from os import path
from typing import Dict, List, Mapping, Optional, Sequence, Union

from yaml import FullLoader as YamlFullLoader, load as yaml_load

yaml_load = partial(yaml_load, Loader=YamlFullLoader)


class JsonLoader:
    def __init__(self):
        self.store = {}

    def load(self, uri):
        file_reader = FileReader(uri)
        return file_reader.contents


_default_json_loader = JsonLoader()


class JsonReference:
    def __init__(self, uri: str, context: Mapping = {}, _loader: JsonLoader = _default_json_loader):
        self.file_name, self.reference = uri.split("#")
        self.context = context
        self.id = uri
        self._loader = _loader

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

        return schema

    def __repr__(self):
        return f"JsonReference({self.id}, {repr(self.context)})"


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

        self._replace_references(contents)

        return contents

    def _replace_references(self, obj, parent: Optional[Union[Dict, List]] = None, uri: List[Union[str, int]] = []) -> None:
        if isinstance(obj, List):
            self._replace_references_in_list(obj, parent, uri)
        elif isinstance(obj, Dict):
            self._replace_references_in_dict(obj, parent, uri)

    def _replace_references_in_dict(self, obj: Dict, parent: Optional[Union[Dict, List]], uri: List[Union[str, int]]) -> None:
        if "$ref" in obj:
            if not parent:
                raise ReferenceError(f"Cannot reference from root path in file {self.file_name}")

            parent[uri[-1]] = self._create_reference(obj)  # if there is a ref in the object rest is ignored

            return

        for key, value in obj.items():
            if not isinstance(value, (dict, list)):
                continue
            self._replace_references(value, obj, uri + [key])

    def _replace_references_in_list(self, obj: List, parent: Optional[Union[Dict, List]], uri: List[Union[str, int]]) -> None:
        for key, value in enumerate(obj):
            if not isinstance(value, (dict, list)):
                continue
            self._replace_references(value, obj, uri + [key])

    def _create_reference(self, ref_obj: Mapping) -> JsonReference:
        ref_str = ref_obj["$ref"]
        file_part, ref_part = ref_str.split("#")
        if not file_part:
            file_part = self.file_name
        else:
            file_part = path.join(path.dirname(self.file_name), file_part)

        full_ref = file_part + "#" + ref_part

        if full_ref not in self.store:
            self.store[full_ref] = JsonReference(full_ref, context=ref_obj)

        return self.store[full_ref]

    @cached_property
    def contents(self) -> dict:
        return self.read()


class OpenApiSchema:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.schema: dict = {}

    @cached_property
    def contents(self) -> dict:
        file = FileReader(self.file_name)
        return file.contents

    def __getitem__(self, reference: str):
        reference_path = reference.lstrip("#").strip("/").split("/")
        schema = self.contents

        for item in reference_path:
            if item not in schema:
                raise KeyError(f"Could not resolve reference {reference}")
            schema = schema[item]

        return schema
