from chocs import Application, HttpRequest, HttpResponse, serve


def authorise_user(req: HttpRequest, next) -> HttpResponse:
    ...
    req.authorised = True

    return next(req)


app = Application(authorise_user)


with app.group("/users") as users_module:

    @users_module.get("/{id}")  # GET /users/{id}
    def get_user(req: HttpRequest) -> HttpResponse:
        ...

    @users_module.post("/")  # POST /users
    def create_user(req: HttpRequest) -> HttpResponse:
        ...


with app.group("/companies") as companies_module:
    ...


serve(app)
