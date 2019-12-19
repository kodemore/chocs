# Chocs [![Build Status](https://travis-ci.org/fatcode/chocs.svg?branch=master)](https://travis-ci.org/fatcode/chocs) [![codecov](https://codecov.io/gh/fatcode/chocs/branch/master/graph/badge.svg)](https://codecov.io/gh/fatcode/chocs) [![Maintainability](https://api.codeclimate.com/v1/badges/d159c53965809f2f4e9d/maintainability)](https://codeclimate.com/github/fatcode/chocs/maintainability)
Chocs is a modern http framework for wsgi compatible servers. Chocs aims to be small, expressive
and robust. 
It provides elegant api for writing fault-proof extensible microservices.  

## Features

 - Elegant and easy api
 - No additional bloat like built-in template engines, session handlers, etc...
 - Compatible with all wsgi servers
 - Loosely coupled components which can be used separately
 - Multipart body parsing
 - Graceful error handling
 - Http middleware support
 - Fast routing

## Installation
```
pip install chocs
```

# Usage

## Quick start

```python
from chocs import HttpRequest, HttpResponse, router, serve

@router.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello {request.attributes['name']}!")

serve()
```

 > Keep in mind `serve()` function is using `bjoern` package, make sure you did include it in your project 
 > dependencies before using it, you can also use any wsgi compatible server of your choice.

## Running application with gunicorn (or any other wsgi server)

```python
# myapp.py
from chocs import Application, HttpRequest, HttpResponse, router

@router.get("/hello/{name}*")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello {request.attributes['name']}!")

app = Application(router)
```

```bash
gunicorn -w 4 myapp:app
```

## Routing
Chocs is shipped with built-in routing module. Easiest way to utilise chocs' routing is to use `chocs.router` object.
`chocs.router` is an instance of module's internal class `chocs.chocs.ApplicationRouter`, it provides simple api where 
each of the function is a decorator corresponding to http method.

```python
from chocs import router, HttpResponse, HttpRequest

@router.get("/hello")
def hello(req: HttpRequest) -> HttpResponse:
    ...
```

The above example will assign hello function to `GET /hello` request. 

Available methods are:
- `delete`
- `get`
- `head`
- `options`
- `patch`
- `post`
- `put`
- `trace`

### Parametrized routes

Routes can contain parametrized parts, parameters must be enclosed within `{` and `}`.

```python
from chocs import router

@router.get("/pet/{id}")
def hello():
    ...
```
Will match following URIs:
 - `/pet/1`
 - `/pet/abc`
 - `/pet/abc1`

When more control is required over accepted parameter's value, additional regex can be passed to function.
Consider following example:

```python
from chocs import router

@router.get("/pet/{id}", id=r"\d+")
def hello():
    ...
```
Above example limits `id` parameters to accept digits only, so `/pet/abc` and `/pet/abc1` will no longer match 
route's pattern.
 
### Wildcarded routes

Asterisk (`*`) can be used to in route's pattern to match any possible combination. Keep in mind routes which DO NOT 
contain wildcards are prioritised over the ones with wildcards.

```python
from chocs import router

@router.get("/pet/*", id)
def hello():
    ...
```

The above example will match following URIs:
- `/pet/a`
- `/pet/a/b/c`
- `/pet/12jd/fds`

## Defining and using custom middleware

Middleware are functions or classes extending `chocs.middleware.Middleware` class. Middleware have access
to request object and next function used to control middleware stack flow. Successful middleware should call
`next` function *(which accepts `chocs.HttpRequest` instance and returns `chocs.HttpReponse`)* and return
valid `chocs.HttpResponse` instance.

Middleware can perform various tasks;
 - making changes in request/response objects ending
 - validating input data
 - authenticating users
 - end request-response cycle
 - connecting to external data source
 
Middleware are different than functions decorated by `router.*` decorators as they got executed every time
request happens and they are not bound to the uri.
 
```python
from chocs import HttpRequest, HttpResponse, serve
from chocs.middleware import MiddlewareHandler

def my_custom_middleware(request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
    name = request.query_string.get("name", "John")
    return HttpResponse(body=f"Hello {name}")

serve(my_custom_middleware)
```

## Request
`chocs.Request` object is an abstraction around wsgi's environ and `wsgi.input` data, providing some additional
information.

#### `Request.headers:dict`
Keeps parsed headers in dict-like object.

#### `Request.body:BytesIO` 
Raw body's data

#### `Request.parsed_body:chocs.message.RequestBody`
Depending on the content type it might be one of the following:
 - `chocs.message.FormBody`
 - `chocs.message.JsonBody`
 - `chocs.message.MultiPartBody`

#### `Request.method:chocs.HttpMethod`
Request's method

#### `Request.uri:str`
Request's uri

#### `Request.query_string:chocs.QueryString`
Dict like object with parsed query string with json forms support.
        
#### `Request.attributes:dict`
Matched route attributes, eg when `/users/john` matches `/users/{name}` route, attributes will
contain `name` key with value of `john`

## Response
`chocs.Response` object 
