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

## Table of Contents

- [Usage](#usage)
  - [Running application with Gunicorn (or any other WSGI server)](#running-application-with-gunicorn-or-any-other-wsgi-server)
  - [Running application in AWS Lambda (Http api or rest api)](#running-application-in-aws-lambda-http-api-or-rest-api)
  - [Routing](#routing)
    - [Parametrized routes](#parametrized-routes)
    - [Wildcard routes](#wildcard-routes)
    - [Route groups](#route-groups)
  - [Middleware](#middleware)
  - [Integration with openapi](#integration-with-openapi)
  - [Transforming request's payload to custom dataclasses](#transforming-requests-payload-to-custom-dataclasses)
    - [Strict mode](#strict-mode)
    - [Non-strict mode, aka: auto hydration](#non-strict-mode-aka-auto-hydration)
    - [Dataclass support library](#dataclass-support-library)
  - [Handling validation errors with custom middleware](#handling-validation-errors-with-custom-middleware)
  - [Defining and using a custom middleware](#defining-and-using-a-custom-middleware)
  - [Request](#request)
  - [Response](#response)
    - [`chocs.Response.status_code: chocs.HttpStatus`](#chocsresponsestatus_code-chocshttpstatus)
  - [Working with cookies](#working-with-cookies)
    - [Reading client cookies](#reading-client-cookies)
    - [Setting cookies](#setting-cookies)
- [Contributing](#contributing)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running tests](#running-tests)
  - [Linting](#linting)
  - [PR](#pr)

# Usage

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

To provide automatic validation for your request based on open api specification, 
use `chocs.middleware.OpenApiMiddleware` middleware bundled with chocs:

```python
from chocs.middleware import OpenApiMiddleware
from chocs import Application, HttpRequest, HttpResponse
from os import path
from dataclasses import dataclass

# absolute path to file containing open api documentation; yaml and json files are supported
openapi_filename = path.join(path.dirname(__file__), "/openapi.yml")

# instantiating application and passing open api middleware
app = Application(OpenApiMiddleware(openapi_filename, validate_body=True, validate_query=True))

# defining our dataclass for better type support
@dataclass()
class Pet:
    id: str
    name: str

# the registered route must correspond to open api route within `path` section.
# if request body is invalid the registered function will not be executed
@app.post("/pets") # `parsed_body` parameter can be used to map request to certain type
def create_pet(request: HttpRequest) -> HttpResponse:
    try: 
        pet = Pet(**request.parsed_body)
    except TypeError:
        return HttpResponse(status=400)
    
    return HttpResponse(pet.name)
```

> Complete integration example can be [found here](./examples/input_validation_with_open_api/openapi.yml)

Chocs automatically validates:
 - request body, `application/json` header must be present for successful validation
 - query string parameters
 - request headers

## Transforming request's payload to custom dataclasses

```python
from chocs.middleware import ParsedBodyMiddleware
from chocs import Application, HttpRequest, HttpResponse
from chocs.dataclasses import asdict
from dataclasses import dataclass
import json

# You can define whether to use strict mode or not for all defined routes.
app = Application(ParsedBodyMiddleware(strict=False))

@dataclass
class Pet:
    id: str
    name: str

@app.post("/pets", parsed_body=Pet) # you can also override default strict mode
def create_pet(request: HttpRequest) -> HttpResponse:
    pet: Pet = request.parsed_body
    assert isinstance(pet, Pet)
    return HttpResponse(json.dumps(asdict(pet)))
```

### Strict mode

Strict mode is using initialiser defined in dataclass. Which means the request data
is simply unpacked and passed to your dataclass, so you have to manually transform 
nested data to dataclasses in order to conform your dataclass interface, for example:

```python
from chocs.middleware import ParsedBodyMiddleware
from chocs import Application, HttpRequest, HttpResponse
from dataclasses import dataclass
from typing import List

app = Application(ParsedBodyMiddleware())

@dataclass
class Tag:
  name: str
  id: str

@dataclass
class Pet:
 id: str
 name: str
 age: int
 tags: List[Tag]
 
 def __post_init__(self):  # post init might be used to reformat your data
  self.age = int(self.age)
  tmp_tags = self.tags
  self.tags = []
  for tag in tmp_tags:
   self.tags.append(Tag(**tag))

@app.post("/pets", parsed_body=Pet) 
def create_pet(request: HttpRequest) -> HttpResponse:
 pet: Pet = request.parsed_body
 assert isinstance(pet.tags[0], Tag)
 assert isinstance(pet, Pet)
 return HttpResponse(pet.name)

```

### Non-strict mode, aka: auto hydration

In non-strict mode `chocs` takes care of instantiating and hydrating your dataclasses. Complex and deeply
nested structures are supported as long as used types are supported by `chocs` hydration mechanism.
List of supported types can be found below in dataclass support library

> Note: __post_init__ method is not called as a part of hydration process.

### Dataclass support library

Dataclass support library is composed of two functions to help with daily tasks while working
with dataclasses. 

#### `chocs.dataclasses.init_dataclass(value: dict, type_name)`

`init_dataclass` function is instantiating dataclass of specified `type_name` and will hydrate the instance 
with values passed in `value` dictionary. Each of the passed dictionary's keys must correspond to dataclass'
attributes in order to be properly interpreted. 

This function support complex and nested hydration, which means if your dataclass aggregates other dataclasses 
or defines complex typing, `init_dataclass` function will respect your type annotations and will cast values 
to match the defined types. 

If attributes in your dataclass do not specify the type value will be hydrated in to a newly created instance as is.

#### `chocs.dataclasses.asdict(value)`

`asdict` is the opposite of `init_dataclass` function, it takes an instance of dataclass as argument, and
extracts its members to a dictionary, so the returned data can be stored as json object orn easily serialised to any other format.

#### Supported data types

`bool`

Passed value is automatically hydrated to boolean with python's built-in `bool` on hydration and extraction.

`dict`

Passed value is automatically hydrated to dict with python's built-in `dict` on hydration and extraction.

`float`

Passed value is automatically hydrated to float with python's built-in `float` on hydration and extraction.

`frozenset`

Passed value is automatically hydrated to frozen set with python's built-in `frozenset` and extracted to `list`.

`int`

Passed value is automatically hydrated to int with python's built-in `int` on hydration and extraction.

`list`

Passed value is automatically hydrated to list with python's built-in `list` on hydration and extraction.

`set`

Passed value is automatically hydrated to set with python's built-in `set` and extracted to `list`.

`str`

Passed value is automatically hydrated to string with python's built-in `str` on hydration and extraction.

`tuple`

Passed value is automatically hydrated to tuple with python's built-in `tuple` and extracted to `list`.

`collections.namedtuple`

Passed value is automatically hydrated to named tuple and extracted to `list`.

`collections.deque`

Passed value is automatically hydrated to an instance of `collections.deque` and extracted to `list`.

`collections.OrderedDict`

Passed value is automatically hydrated to an instance of `collections.OrderedDict` and extracted to `dict`.

`datetime.date`

Passed value must be valid ISO-8601 date string, then it is automatically hydrated to an instance of `datetime.date` 
class and extracted to ISO-8601 format compatible string.

`datetime.datetime`

Passed value must be valid ISO-8601 date time string, then it is automatically hydrated to an instance of `datetime.datetime` 
class and extracted to ISO-8601 format compatible string.

`datetime.time`

Passed value must be valid ISO-8601 time string, then it is automatically hydrated to an instance of `datetime.time` 
class and extracted to ISO-8601 format compatible string.

`datetime.timedelta`

Passed value must be valid ISO-8601 duration string, then it is automatically hydrated to an instance of `datetime.timedelta`
class and extracted to ISO-8601 format compatible string.

`decimal.Decimal`

Passed value must be a string containing valid decimal number representation, for more please read python's manual
about [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal), on extraction value is
extracted back to string.

`enum.Enum`

Supports hydration of all instances of `enum.Enum` subclasses as long as value can be assigned
to one of the members defined in the specified `enum.Enum` subclass. During extraction the value is
extracted to value of the enum member.

`enum.IntEnum`

Same as `enum.Enum`.

`typing.Any`

Passed value is unchanged during hydration and extraction process.

`typing.AnyStr`

Same as `str`

`typing.Deque`

Same as `collection.dequeue` with one exception, if subtype is defined, eg `typing.Deque[int]` each item inside queue
is hydrated accordingly to subtype.

`typing.Dict`

Same as `dict` with exception that keys and values are respectively hydrated and extracted to match
annotated type.

`typing.FrozenSet`

Same as `frozenset` with exception that values of a frozen set are respectively hydrated and extracted to
match annotated type.

`typing.List`

Same as `list` with exception that values of a list are respectively hydrated and extracted to match annotated type.

`typing.NamedTuple`

Same as `namedtuple`.

`typing.Optional`

Optional types can carry additional `None` value which chocs' hydration process will respect, so for example 
if your type is `typing.Optional[int]` `None` value is not hydrated to `int`.

`typing.Set`

Same as `set` with exception that values of a set are respectively hydrated and extracted to match annotated type.

`typing.Tuple`

Same as `tuple` with exception that values of a set are respectively hydrated and extracted to match annotated types.
Ellipsis operator (`...`) is also supported.

`typing.TypedDict`

Same as `dict` but values of a dict are respectively hydrated and extracted to match annotated types. 


## Handling validation errors with custom middleware

By default, if validation fails users will see `500 response`. This behavior can be changed if custom middleware that
catches validation errors is defined and used in application.

## Defining and using a custom middleware
 
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
[Moved to wiki](https://github.com/kodemore/chocs/wiki/Request)

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
