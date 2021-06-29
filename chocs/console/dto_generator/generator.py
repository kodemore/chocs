from typing import Callable, Dict, List
from os import path
import datetime
import re

from chocs.json_schema.json_schema import OpenApiSchema
from .processor import (
    AstPropertyNode,
    SchemaProcessor,
    AstTypeNode,
    AstClassNode,
    AstReferenceTypeNode,
    AstListTypeNode,
)


def to_snake_case(text: str) -> str:
    snake_cased = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", snake_cased).lower()


class DtoGenerator:
    def __init__(
        self,
        openapi_path: str,
        out: str,
        snake_case: bool = False,
        class_suffix: str = "",
    ):
        openapi_path = path.realpath(openapi_path)
        self.openapi_schema = OpenApiSchema(openapi_path)
        self.openapi_path = openapi_path
        self.snake_case = snake_case
        self.class_suffix = class_suffix
        self.out = out

    def generate(self, log_info: Callable, log_error: Callable) -> None:
        schema_processor = SchemaProcessor(self.openapi_schema)
        ast_classes = self._order_ast_classes(schema_processor.process())

        module_str = (
            '"""\n'
            "Do not edit! \n\n"
            f"This file was automatically generated from: \n{self.openapi_path}\n\n"
            f"Generation time: \n{datetime.datetime.utcnow()} \n"
            '"""\n\n'
        )
        module_str += "import datetime\n"
        module_str += "import typing\n"
        module_str += "import decimal\n"
        module_str += "import ipaddress\n"
        module_str += "import dataclasses\n"

        for ast_class in ast_classes:
            log_info(f"Generating class `{ast_class.class_name + self.class_suffix}` from `{ast_class.id}`")
            try:
                module_str += "\n\n" + self._generate_class(ast_class)
            except Exception as e:
                log_error(f"Error occurred during generation {e}.")
                return

        with open(self.out, "w") as module_file:
            module_file.write(module_str)

    def _generate_class(self, ast_class: AstClassNode) -> str:
        out = "@dataclasses.dataclass()\n"
        out += f"class {ast_class.class_name + self.class_suffix}"
        if ast_class.parent_classes:
            out += "(" + ",".join([parent.class_name + self.class_suffix for parent in ast_class.parent_classes]) + ")"

        out += ":\n"

        if not ast_class.properties:
            return out + "    pass\n"

        return out + self._generate_properties(ast_class.properties)

    def _generate_properties(self, properties: Dict[str, AstPropertyNode]) -> str:
        out = ""
        for property_ in properties.values():
            out += "    " + self._generate_property(property_)
            out += "\n"

        return out

    def _generate_property(self, property_: AstPropertyNode) -> str:
        if self.snake_case:
            out = f"{to_snake_case(property_.name)}: "
        else:
            out = f"{property_.name}: "
        property_type = self._generate_type(property_.type)
        if property_.optional:
            out += f"typing.Optional[{property_type}]"
        else:
            out += property_type
        return out

    def _generate_type(self, type_: AstTypeNode) -> str:

        if isinstance(type_, AstReferenceTypeNode):
            return f"'{type_.reference.class_name + self.class_suffix}'"
        if isinstance(type_, AstListTypeNode):
            return self._generate_list_type(type_)
        return type_.name

    def _generate_list_type(self, type_: AstListTypeNode) -> str:
        if len(type_.items) > 1:
            return f"typing.Tuple[{','.join([self._generate_type(item_type) for item_type in type_.items])}]"

        if type_.unique:
            return f"typing.Set[{self._generate_type(type_.items[0])}]"

        return f"typing.List[{self._generate_type(type_.items[0])}]"

    def _order_ast_classes(self, ast_classes: Dict[str, AstClassNode]) -> List[AstClassNode]:
        ast_classes_list = ast_classes.values()

        # Classes without parent class
        ordered_list = [ast_class for ast_class in ast_classes_list if not ast_class.parent_classes]

        while len(ordered_list) < len(ast_classes_list):
            for ast_class in ast_classes_list:
                if ast_class in ordered_list:
                    continue

                for parent_class in ast_class.parent_classes:
                    if parent_class not in ordered_list:
                        break

                ordered_list.append(ast_class)

        return ordered_list
