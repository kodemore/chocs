from cheroot.wsgi import Server
from typing import Callable


def wsgi_serve(
    wsgi_handler: Callable,
    host: str = "127.0.0.1",
    port: int = 80,
    workers: int = 1,
) -> None:
    wsgi_server = Server((host, port), wsgi_handler, numthreads=workers)
    wsgi_server.start()
