from cleo import Application
from chocs.__version__ import __version__
from .generate_dto import GenerateDtoCommand

application = Application(
    name="chocs",
    version=__version__,
)
application.add(GenerateDtoCommand())


def main() -> None:
    application.run()


if __name__ == "__main__":
    main()
