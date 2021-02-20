import gunicorn.app.base

from chocs import Application, HttpRequest, HttpResponse, create_wsgi_handler

app = Application()


@app.post("/hello")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(body=f"Hello {request.parsed_body['name']}!")


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    options = {
        "bind": "%s:%s" % ("127.0.0.1", "8080"),
        "workers": 1,
    }
    StandaloneApplication(create_wsgi_handler(app), options).run()
