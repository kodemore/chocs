# Chocs [![Build Status](https://travis-ci.org/fatcode/chocs.svg?branch=master)](https://travis-ci.org/fatcode/chocs) [![codecov](https://codecov.io/gh/fatcode/chocs/branch/master/graph/badge.svg)](https://codecov.io/gh/fatcode/chocs) [![Maintainability](https://api.codeclimate.com/v1/badges/d159c53965809f2f4e9d/maintainability)](https://codeclimate.com/github/fatcode/chocs/maintainability)
Chocs is a modern HTTP framework for WSGI compatible servers. Chocs aims to be small, expressive, and robust. 
It provides an elegant API for writing fault-proof, extensible microservices.  

## Features

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
from chocs import HttpRequest, HttpResponse, router, serve

@router.get("/hello/{name}")
def hello(request: HttpRequest) -> HttpResponse:
    return HttpResponse(f"Hello {request.attributes['name']}!")

serve()
```

 > Keep in mind that the `serve()` function is using the `bjoern` package, so make sure you included it in your project 
 > dependencies before using it. You are able to use any WSGI compatible server.

## Running application with Gunicorn (or any other WSGI server)

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
Chocs is shipped with a built-in routing module. The easiest way to utilise chocs' routing is to use `chocs.router` object.
`chocs.router` is an instance of the module's internal class `chocs.chocs.ApplicationRouter`, which provides a simple API 
where each function is a decorator corresponding to an HTTP method.

```python
from chocs import router, HttpResponse, HttpRequest

@router.get("/hello")
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
from chocs import router

@router.get("/pet/{id}")
def hello():
    ...
```
Will match the following URIs:
 - `/pet/1`
 - `/pet/abc`
 - `/pet/abc1`

Advanced matching can be achieved by passing a regex to the function.
Consider the following example:

```python
from chocs import router

@router.get("/pet/{id}", id=r"\d+")
def hello():
    ...
```
This restricts the `id` parameter to accept only digits, so `/pet/abc` and `/pet/abc1` will no longer match route's 
pattern.
 
### Wildcard routes

Asterisks (`*`) can be used in the route's pattern to match any possible combination. Keep in mind that routes which 
_do not_ contain wildcards are prioritised over routes with wildcards.

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

## Defining and using a custom middleware

Middleware are functions or classes that inherit `chocs.middleware.Middleware`. Middlewares have access to the request 
object and the next function is used to control middleware stack flow. Successful middleware execution should call
the `next` function *(which accepts a `chocs.HttpRequest` instance and returns `chocs.HttpReponse`)* and return a
valid `chocs.HttpResponse` instance.

Middlewares can perform various tasks:
 - Making changes in request/response objects ending
 - Validating input data
 - Authenticating users
 - End request-response cycle
 - Connecting to external data sources
 
Middlewares are different to functions decorated by `router.*` decorators as they are executed every time a request 
happens and they are not bound to the URI.
 
```python
from chocs import HttpRequest, HttpResponse, serve
from chocs.middleware import MiddlewareHandler

def my_custom_middleware(request: HttpRequest, next: MiddlewareHandler) -> HttpResponse:
    name = request.query_string.get("name", "John")
    return HttpResponse(body=f"Hello {name}")

serve(my_custom_middleware)
```

## Request
`chocs.Request` object is an abstraction around WSGI's environment and `wsgi.input` data, providing some additional
information.

#### `Request.headers:dict`
Keeps parsed headers in dict-like object.

#### `Request.body:BytesIO` 
Raw body data

#### `Request.parsed_body:chocs.message.RequestBody`
Depending on the content type it could be one of the following:
 - `chocs.message.FormBody`
 - `chocs.message.JsonBody`
 - `chocs.message.MultiPartBody`

#### `Request.method:chocs.HttpMethod`
The request's method

#### `Request.uri:str`
The request's URI

#### `Request.query_string:chocs.QueryString`
A dict like object with parsed query string with JSON forms support
        
#### `Request.attributes:dict`
Matched route attributes, for example when `/users/john` matches the `/users/{name}` route, attributes will contain a 
`name` key with a value of `john`

## Response
`chocs.Response` object 
