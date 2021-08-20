from io import BytesIO
from json import dumps as json_dumps
from typing import Dict, Optional, Union

from chocs.http.http_headers import HttpHeaders
from chocs.http.http_method import HttpMethod
from chocs.http.http_query_string import HttpQueryString
from chocs.http.http_request import HttpRequest
from chocs.http.http_response import HttpResponse
from .application import Application


class TestClient:
    def __init__(self, application: Application):
        self.application = application

    def get(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.GET, path, body, json, headers))

    def post(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.POST, path, body, json, headers))

    def patch(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.PATCH, path, body, json, headers))

    def delete(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.DELETE, path, body, json, headers))

    def put(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.PUT, path, body, json, headers))

    def options(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.OPTIONS, path, body, json, headers))

    def head(
        self,
        path: str,
        body: Union[Optional[BytesIO], str] = None,
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpResponse:

        return self.application(self._create_request(HttpMethod.HEAD, path, body, json, headers))

    @staticmethod
    def _create_request(
        method: HttpMethod,
        path: str,
        body: Union[Optional[BytesIO], str],
        json: Optional[Dict] = None,
        headers: Optional[Union[HttpHeaders, Dict[str, str]]] = None,
    ) -> HttpRequest:
        if headers is None:
            headers = {}

        if json:
            body = json_dumps(json)
            headers["Content-Type"] = "application/json"

        path_parts = path.split("?")
        uri = path_parts[0]
        query_string = HttpQueryString(path_parts[1] if len(path_parts) > 1 else "")

        return HttpRequest(
            method=method,
            path=uri,
            body=body,
            headers=headers,
            query_string=query_string,
        )
