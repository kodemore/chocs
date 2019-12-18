# Chocs
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
