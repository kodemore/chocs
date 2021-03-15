from typing import Callable, Dict, Any

from gunicorn.app.base import BaseApplication


class GunicornApplication(BaseApplication):
    def __init__(self, wsgi_handler: Callable, options: Dict[str, Any] = None):
        self.options = options or {}
        self.wsgi_handler = wsgi_handler
        super().__init__()

    def load_config(self) -> None:
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> Any:
        return self.wsgi_handler

    def init(self, parser, opts, args):
        pass


def wsgi_serve(
    wsgi_handler: Callable,
    host: str = "127.0.0.1",
    port: int = 80,
    workers: int = 1,
) -> None:
    options = {
        "bind": f"{host}:{port}",
        "workers": workers,
    }
    server = GunicornApplication(wsgi_handler, options)
    server.run()
