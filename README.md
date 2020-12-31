# Chocs [![PyPI version](https://badge.fury.io/py/chocs.svg)](https://pypi.org/project/chocs/) ![Release](https://github.com/kodemore/chocs/workflows/Release/badge.svg) ![Linting and Tests](https://github.com/kodemore/chocs/workflows/Linting%20and%20Tests/badge.svg) [![codecov](https://codecov.io/gh/kodemore/chocs/branch/master/graph/badge.svg)](https://codecov.io/gh/kodemore/chocs) [![Maintainability](https://api.codeclimate.com/v1/badges/9e3c979283b2361a9174/maintainability)](https://codeclimate.com/github/kodemore/chocs/maintainability)
Chocs is a modern HTTP framework for building AWS HTTP API/REST API and WSGI compatible applications. 
Chocs aims to be small, expressive, and robust. 
It provides an elegant API for writing fault-proof, extensible microservices.  

## Features

 - AWS Serverless integration
 - Open api integration  
 - Elegant and easy API
 - No additional bloat like built-in template engines, session handlers, etc.
 - Compatible with all WSGI servers
 - Loosely coupled components which can be used separately
 - Multipart body parsing
 - Graceful error handling
 - HTTP middleware support
 - Fast routing

## Installation
```
pip install chocs
```

# Usage

## Quick start

```python
from chocs import Application
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import serve


http = Application()

@http.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello {request.path_parameters.get('name')}!")

serve(http)
```

 > Keep in mind that the `serve()` function is using the `bjoern` package, so make sure you included it in your project 
 > dependencies before using it. You are able to use any WSGI compatible server.

## Running application with Gunicorn (or any other WSGI server)

```python
# myapp.py
from chocs import Application
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import create_wsgi_handler


http = Application()


@http.get("/hello/{name}*")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello {request.path_parameters.get('name')}!")

app = create_wsgi_handler(http, debug=False)
```

```bash
gunicorn -w 4 myapp:app
```

## Running application in AWS Lambda (Http api or rest api)

`handler.py`
```python
import logging

from chocs import HttpRequest
from chocs import HttpResponse
from chocs import Application

logger = logging.getLogger()
logger.setLevel(logging.INFO)


http = Application()


@http.get("/hello/{name}")
def hello_handler(request: HttpRequest) -> HttpResponse:
    logger.info("Hello AWS!")
    logger.info(request.attributes.get("aws_context"))
    logger.info(request.attributes.get("aws_event"))
    return HttpResponse(f"Hello {request.path_parameters.get('name')}")


__all__ = ["hello_handler"]
```

`serverless.yml`
```yaml
service: aws-hello-name

provider:
  name: aws
  runtime: python3.8

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true

functions:
  hello_name:
    handler: handler.hello_handler
    events:
      - httpApi:
          method: GET
          path: /hello/{name}
```

```bash
serverless deploy
```

## Routing
Chocs is shipped with a built-in routing module. The easiest way to utilise chocs' routing is to use `chocs.router` object.
`chocs.router` is an instance of the module's internal class `chocs.application.Application`, which provides a simple API 
where each function is a decorator corresponding to an HTTP method.

```python
from chocs import Application, HttpResponse, HttpRequest


http = Application()


@http.get("/hello")
def hello(req: HttpRequest) -> HttpResponse:
    ...
```

The above example will assign the hello function to handle a `GET /hello` request. 

Available methods:
- `delete`
- `get`
- `head`
- `options`
- `patch`
- `post`
- `put`
- `trace`

### Parametrized routes

Routes can contain parameterised parts. Parameters must be enclosed within `{` and `}`.

```python
from chocs import Application

http = Application()


@http.get("/pet/{id}")
def hello():
    ...
```
Will match the following URIs:
 - `/pet/1`
 - `/pet/abc`
 - `/pet/abc1`
 
### Wildcard routes

Asterisks (`*`) can be used in the route's pattern to match any possible combination. Keep in mind that routes which 
_do not_ contain wildcards are prioritised over routes with wildcards.

```python
from chocs import Application

http = Application()


@http.get("/pet/*", id)
def hello():
    ...
```

The above example will match following URIs:
- `/pet/a`
- `/pet/a/b/c`
- `/pet/12jd/fds`

### Route groups

Chocs supports route groups. Route groups is implemented through [context lib interface](https://docs.python.org/3/library/contextlib.html).
If you need to split your application in smaller chunks with standalone req/res handlers consider the
following example:

```python
from threading import Thread

from chocs.wsgi import serve 
from chocs import Application
from chocs import HttpRequest
from chocs import HttpResponse

main_app = Application()

with main_app.group("/users/{id}") as user_module:
    
    @user_module.post("/profile_picture")  # POST /users/{id}/profile_pictures
    def create_profile_picture(request: HttpRequest) -> HttpResponse:
        ...
    
    @user_module.get("/profile_picture")  # GET /users/{id}/profile_pictures
    def get_profile_picture(request: HttpRequest) -> HttpResponse:
        ...
    
    @user_module.get("/badges") # GET /users/{id}/badges
    def badges(request: HttpRequest) -> HttpResponse:
        ...

with main_app.group("/payments") as payment_module:

    @payment_module.get("/analytics") # GET /payments/analytics
    def get_analytics(request: HttpRequest) -> HttpResponse:
        ...

if __name__ == '__main__':
    def wsgi_user_module():
        serve(user_module, port=8081)
    def wsgi_payment_module():
        serve(payment_module, port=8082)

    Thread(target=wsgi_user_module).start()
    payment_module()
```

The above example shows how to run two different modules, which support their own routes
on two different ports in the one process.

## Middleware

Middleware are functions or classes that inherit `chocs.Middleware`. Middlewares have access to the request object
and the `next` function which can be used to control middleware stack flow. Successful middleware execution should call
the `next` function which accepts a `chocs.HttpRequest` instance and returns `chocs.HttpReponse`.

Middlewares can perform various tasks:
- Making changes in request/response objects ending
- Validating input data
- Authenticating users
- End request-response cycle
- Connecting to external data sources

## Integration with openapi

Chocs provides middleware which can be used to validate input data and simplify working with 
inputs by mapping them to dataclasses. To provide automatic validation for your request based
on open api specification, instance of `chocs.middleware.OpenApiMiddleware` has to be created:

```python
from chocs.middleware import OpenApiMiddleware
from chocs import Application, HttpRequest, HttpResponse
from os import path
from dataclasses import dataclass

# absolute path to file containing open api documentation; yaml and json files are supported
openapi_filename = path.join(path.dirname(__file__), "/openapi.yml")

# instantiating application and passing open api middleware
app = Application(OpenApiMiddleware(openapi_filename))

# defining our dataclass for better type support
@dataclass()
class Pet:
    id: str
    name: str

# the registered route must correspond to open api route within `path` section.
# if request body is invalid the registered function will not be executed
@app.post("/pets", parsed_body=Pet) # `parsed_body` parameter can be used to map request to certain type
def create_pet(request: HttpRequest) -> HttpResponse:
    # if request body is valid `request.parsed_body` will be instance of a Pet
    assert isinstance(request.parsed_body, Pet)
    
    pet = request.parsed_body
    return HttpResponse(pet.name)
```

Open api file used in the example above can be [found here](./examples/input_validation_with_open_api/openapi.yml)

### Handling validation errors with custom middleware

By default, if validation fails users will see `500 response`. This behavior can be changed if custom middleware that
catches validation errors is defined and used in application.

### Defining and using a custom middleware
 
The following code defines simple function middleware to catch validation errors when they appear and notifies users:

```python
from chocs.middleware import OpenApiMiddleware
from chocs.json_schema.errors import ValidationError
from chocs import Application, HttpRequest, HttpResponse
from dataclasses import dataclass
import json
from typing import Callable
from os import path

openapi_filename = path.join(path.dirname(__file__), "/openapi.yml")


# middleware must always accept two parameters; HttpRequest and Callable and return HttpResponse
def handle_errors(request: HttpRequest, next: Callable) -> HttpResponse:
    try:
        return next(request) # we pass request further to middleware pipeline
    except ValidationError as error: # if exception is thrown it is caught here and new response is generated instead
        json_response = {
            "code": error.code,
            "message": str(error),
        }
        return HttpResponse(json.dumps(json_response), status=422)
    
# error handling middleware must go before open api one to catch errors thrown inside open api middleware
app = Application(handle_errors, OpenApiMiddleware(openapi_filename))

@dataclass()
class Pet:
  id: str
  name: str

@app.post("/pets", parsed_body=Pet)
def create_pet(request: HttpRequest) -> HttpResponse:
  assert isinstance(request.parsed_body, Pet)

  pet = request.parsed_body
  return HttpResponse(pet.name)
```

Full working example can be found inside [examples directory](./examples/input_validation_with_open_api)

## Request
`chocs.Request` object is an abstraction around WSGI's environment and `wsgi.input` data with handy interface 
to ease everyday work.

#### `chocs.Request.headers:chocs.HttpHeaders (read-only)`
Keeps parsed headers in dict-like object.

#### `chocs.Request.body:io.BytesIO` 
Raw body data

#### `chocs.Request.parsed_body:chocs.HttpMessage`
Depending on the content type it could be one of the following:
 - `chocs.FormHttpMessage`
 - `chocs.JsonHttpMessage`
 - `chocs.MultipartHttpMessage`
 - `chocs.YamlHttpMessage`

#### `chocs.Request.as_dict(): dict`
Tries to convert request body to a dict and returns it.

> Note this will only work with json and yaml content types.

#### `chocs.Request.as_str(): str`
Returns request content as a string.
 
#### `chocs.Request.cookies:typing.List[chocs.HttpCookie]` 
Request's cookies

#### `chocs.Request.method:chocs.HttpMethod`
The request's method

#### `chocs.Request.path:str`
The request's path

#### `chocs.Request.query_string:chocs.HttpQueryString`
A dict like object with parsed query string with JSON forms support
        
#### `chocs.Request.path_parameters:dict`
Matched route parameters, for example when `/users/john` matches the `/users/{name}` route, parameters will contain a 
`name` key with a value of `john`

#### `chocs.Request.attributes:dict`
Other environmental or custom attributes attached to the request object, eg.: `aws_event` or `aws_context`
when running chocs app as aws lambda.

## Response
`chocs.Response` object is a part of request-response flow and it is required to be returned by all functions
decorated with `router.*` method. Instance of the response class is recognised by `chocs.Application` and used to 
generate real response served to your clients.

#### `chocs.Response.body: io.BytesIO` 
Body served to server's clients.

### `chocs.Response.status_code: chocs.HttpStatus`
Valid response code, instance of `chocs.HttpStatus` enum can be used or just a status code's number.

#### `chocs.Response.cookies:chocs.HttpCookieJar` 
Response's cookies

#### `chocs.Response.write(body: Union[bytes, str, bytearray])`
Write bytes to response body

#### `chocs.Response.close()`
Makes body non-writable.

#### `chocs.Response.writable: bool`
Indicates whether response's body is writable.

#### `chocs.Response.parsed_body:chocs.HttpMessage`
Depending on the content type it could be one of the following:
- `chocs.FormHttpMessage`
- `chocs.JsonHttpMessage`
- `chocs.MultipartHttpMessage`
- `chocs.YamlHttpMessage`

#### `chocs.Response.as_dict(): dict`
Tries to convert response body to a dict and returns it.

> Note this will only work with json and yaml content types.

#### `chocs.Response.as_str(): str`
Returns response content as a string.

## Working with cookies

`chocs.HttpCookieJar` object takes care of cookie handling. It can be accessed in dict-like manner, when item is requested,
instance of `chocs.HttpCookie` is returned to user. 

Cookies can be set either by passing string value to the `chocs.CookieJar`'s key, or by calling `chocs.CookieJar.append` 
method which accepts instance of `chocs.Cookie`.

### Reading client cookies

Cookies can be easily accessed from `chocs.Request.cookies` object which is injected as a parameter to each function 
registered as route handler. Consider the following example:

```python
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import Application
from chocs import serve

http = Application()


@http.get("/cookies")
def read_cookies(request: HttpRequest) -> HttpResponse:

    message = "Hello"
    if "user_name" in request.cookies:
        message += f", {str(request.cookies['user_name'])}"
    message += "!"

    return HttpResponse(body=message)

serve(http)
```

### Setting cookies
```python
from datetime import datetime

from chocs import HttpCookie
from chocs import HttpRequest
from chocs import HttpResponse
from chocs import Application
from chocs import serve

http = Application()


@http.get("/cookies")
def read_cookies(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(body="Hi! I have baked some cookies for ya!")
    response.cookies['simple-cookie'] = "Simple cookie for simple people"
    response.cookies.append(HttpCookie("advanced-cookie", "This cookie will expire in 2021-01-01", expires=datetime(2021, 1, 1)))
    return response

serve(http)
```

# Contributing

## Prerequisites

- libev
- python 3.8
- docker

## Installation

`poetry install`

## Running tests

`poetry run pytest`

## Linting

```shell
poetry run black .
poetry run isort .
poetry run mypy .
```

## PR 
