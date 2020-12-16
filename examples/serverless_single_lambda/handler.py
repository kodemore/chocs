from chocs import Application, HttpMethod, HttpRequest, HttpResponse, HttpStatus


def authorise_user(req: HttpRequest, next) -> HttpResponse:

    ...
    req.authorised = True

    return next(req)


def validate_input(req: HttpRequest, next) -> HttpResponse:
    validator = req.route.config.validator

    valid = False
    ...
    if req.method is HttpMethod.POST:
        ...
    if not valid:
        return HttpResponse(status=HttpStatus.UNPROCESSABLE_ENTITY)

    return next(req)


app = Application(authorise_user, validate_input)


with app.group("/users") as users_module:

    @users_module.get("/{id}")  # GET /users/{id}
    def get_user(req: HttpRequest) -> HttpResponse:
        ...

    @users_module.post("/")  # POST /users
    def create_user(req: HttpRequest) -> HttpResponse:
        ...


with app.group("/companies") as companies_module:
    ...
