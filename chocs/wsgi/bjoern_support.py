from typing import Callable

from bjoern import run


def wsgi_serve(
    wsgi_handler: Callable,
    host: str = "127.0.0.1",
    port: int = 80,
    workers: int = 1,
) -> None:
    if workers >= 1:
        run(wsgi_handler, host, port)
