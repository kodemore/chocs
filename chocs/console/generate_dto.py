from cleo import Command
from .dto_generator.generator import DtoGenerator
from os import path


class GenerateDtoCommand(Command):
    """
    Generate dto classes from openapi file.

    generate:dto
        { openapi-path : Path to openapi.yml file }
        { --module-path=dto.py : Path to module file where generated classes will be stored, keep in mind this file will be automatically replaced! }

    """

    def handle(self):
        openapi_path = self.argument('openapi-path')
        module_path = self.option('module-path')

        if not path.isfile(openapi_path):
            self.line_error(f"<error>Could not read openapi file `{openapi_path}`.</error>")
            return 1

        if not path.isfile(module_path):
            self.line_error(f"<error>Output module `{module_path}` does not exists.</error>")
            return 1

        self.info(f"Generating dto classes from `{openapi_path}`...")

        dto_generator = DtoGenerator(openapi_path, module_path)
        dto_generator.generate(lambda msg: self.info(msg), lambda msg: self.line_error(msg))
