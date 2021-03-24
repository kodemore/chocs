from typing import Any, Dict, List, Union

from chocs.json_schema.json_schema import JsonReference, OpenApiSchema


class AstTypeNode:
    name: str

    def __init__(self, name: str):
        self.name = name


class AstReferenceTypeNode(AstTypeNode):
    reference: "AstClassNode"

    def __init__(self, reference: "AstClassNode"):
        self.reference = reference
        super().__init__(reference.id)


class AstListTypeNode(AstTypeNode):
    items: List[AstTypeNode]
    unique: bool = False

    def __init__(self, name: str):
        super().__init__(name)
        self.items = []


class AstPropertyNode:
    name: str
    type: AstTypeNode
    optional: bool = True

    def __init__(self, name: str):
        self.name = name


class AstClassNode:
    id: str
    parent_classes: List["AstClassNode"]
    properties: Dict[str, AstPropertyNode]

    def __init__(self, class_id: str):
        self.id = class_id
        self.parent_classes = []
        self.properties = {}

    @property
    def class_name(self) -> str:
        return self.id.split("/")[-1]


class SchemaProcessor:
    def __init__(self, schema: OpenApiSchema):
        self.schema = schema
        self.components = self.schema.query("/components/schemas")
        self._processed_classes: Dict[str, AstClassNode] = {}

    def process(self) -> Dict[str, AstClassNode]:
        for name, schema in self.components.items():
            ref = f"{self.schema.file_name}#/components/schemas/{name}"
            self._process_class_node(ref, schema)

        return self._processed_classes

    def _process_class_node(self, ref: str, schema: Union[JsonReference, dict]) -> AstClassNode:
        if ref in self._processed_classes:
            return self._processed_classes[ref]

        class_node = AstClassNode(ref)
        self._processed_classes[ref] = class_node

        if "properties" in schema:
            self._process_properties_nodes(class_node, schema)

        if "allOf" in schema:
            for sub_schema in schema["allOf"]:
                if isinstance(sub_schema, JsonReference):
                    class_node.parent_classes.append(self._process_class_node(sub_schema.id, sub_schema.data))

                    continue

                if "type" in sub_schema and sub_schema["type"] == "object":
                    self._process_properties_nodes(class_node, sub_schema)
                    continue

                raise RuntimeError(f"Unexpected value inside component {ref}.allOf")

        return class_node

    def _process_properties_nodes(self, dto_class: AstClassNode, schema: Union[JsonReference, dict]) -> None:
        if "properties" not in schema:
            return

        for property_name, property_schema in schema["properties"].items():
            dto_property = AstPropertyNode(property_name)
            dto_class.properties[property_name] = dto_property

            if property_name in schema.get("required", []):
                dto_property.optional = False

            try:
                dto_property.type = self._process_type_node(property_schema)
            except RuntimeError as e:
                raise RuntimeError(f"Cannot process property {property_name}") from e

    def _process_type_node(self, schema: Union[JsonReference, Dict[str, Any]]) -> AstTypeNode:
        if isinstance(schema, JsonReference):
            return AstReferenceTypeNode(self._process_class_node(schema.id, schema))

        if "type" not in schema:
            return AstTypeNode("str")

        if schema["type"] == "object":
            return AstTypeNode("typing.Dict[str, typing.Any]")

        if schema["type"] == "integer":
            return AstTypeNode("int")

        if schema["type"] in ("float", "number"):
            return AstTypeNode("float")

        if schema["type"] == "boolean":
            return AstTypeNode("bool")

        if schema["type"] == "string":
            if "format" not in schema:
                return AstTypeNode("str")

            if schema["format"] == "date":
                return AstTypeNode("datetime.date")

            if schema["format"] == "date-time":
                return AstTypeNode("datetime.datetime")

            if schema["format"] == "time":
                return AstTypeNode("datetime.time")

            if schema["format"] == "ip-address-v4":
                return AstTypeNode("ipaddress.IPv4Address")

            if schema["format"] == "ip-address-v6":
                return AstTypeNode("ipaddress.IPv6Address")

            if schema["format"] == "time-duration":
                return AstTypeNode("datetime.timedelta")

            if schema["format"] == "decimal":
                return AstTypeNode("decimal.Decimal")

            if schema["format"] == "byte":
                return AstTypeNode("bytes")

            return AstTypeNode("str")

        if schema["type"] == "array":
            property_type = AstListTypeNode("list")

            if "uniqueItems" in schema:
                property_type.unique = schema["uniqueItems"]

            if "items" not in schema:
                property_type.items.append(AstTypeNode("typing.Any"))
                return property_type

            if isinstance(schema["items"], list):
                property_type.items = [self._process_type_node(item_schema) for item_schema in schema["items"]]
            else:
                property_type.items = [self._process_type_node(schema["items"])]
            return property_type

        raise RuntimeError(f"Unknown property type {schema['type']}")
