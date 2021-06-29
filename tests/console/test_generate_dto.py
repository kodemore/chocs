from os import path

import pytest
from cleo import Application, Command, CommandTester

from chocs.console.generate_dto import GenerateDtoCommand
from chocs.dataclasses.support import init_dataclass


def get_command_tester(command_class: Command, command_name: str) -> CommandTester:
    application = Application()
    application.add(command_class)
    command = application.find(command_name)
    command_tester = CommandTester(command)
    return command_tester


def test_fail_command_invalid_openapi() -> None:
    command_tester = get_command_tester(GenerateDtoCommand(), "generate:dto")
    result = command_tester.execute("a")
    assert result == 1
    assert command_tester.io.fetch_error() == "Could not read openapi file `a`.\n"


def test_fail_command_invalid_output_module() -> None:
    command_tester = get_command_tester(GenerateDtoCommand(), "generate:dto")
    openapi_path = path.dirname(__file__) + "/../fixtures/openapi.yml"
    result = command_tester.execute(openapi_path)
    assert result == 1
    assert (
        command_tester.io.fetch_error() == "Output module `dto.py` does not exists.\n"
    )


def test_generate_dtos() -> None:
    command_tester = get_command_tester(GenerateDtoCommand(), "generate:dto")
    openapi_path = path.dirname(__file__) + "/../fixtures/openapi.yml"
    dto_module = path.dirname(__file__) + "/../fixtures/generated_dtos.py"
    result = command_tester.execute(f"{openapi_path} --module-path={dto_module}")

    assert not result

    try:
        from tests.fixtures import generated_dtos
    except Exception:
        pytest.fail("Failed to generate valid dto classes")
        return

    pet_tag = init_dataclass({"name": "Test Tag", "id": 12}, generated_dtos.PetTag)
    assert isinstance(pet_tag, generated_dtos.PetTag)

    pet = init_dataclass({"id": 123, "name": "Boo"}, generated_dtos.Pet)
    assert isinstance(pet, generated_dtos.Pet)
    assert isinstance(pet, generated_dtos.NewPet)
