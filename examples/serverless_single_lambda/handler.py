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
        return HttpResponse(HttpStatus.UNPROCESSABLE_ENTITY)

    return next(req)


def sentry_error_handler(req: HttpRequest, next) -> HttpResponse:

    try:
        res = next(req)
    except Er



app = Application(authorise_user, validate_input)


with app.group('/users') as users_module:

    @users_module.get('/{id}', validator=Dupa)  # GET /users/{id}
    def get_user(req: HttpRequest, db: wio) -> HttpResponse:
        ...

    @users_module.post("/")  # POST /users
    def create_user(req: HttpRequest) -> HttpResponse:
        ...

    with users_module.group("/aasdasda/sadasdasdas/dasdasdadsasfsdasfdaf/adfasdfasd") as users_pict_module:
        ...


with app.group("/companies") as companies_module:
    ...


serve(app)
