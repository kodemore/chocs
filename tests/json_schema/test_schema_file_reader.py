from chocs.json_schema import FileReader
from os import path


def test_can_read_yaml_file() -> None:
    reader = FileReader(path.dirname(__file__) + "/../fixtures/openapi.yml")
    assert reader.read()
    assert reader._read
