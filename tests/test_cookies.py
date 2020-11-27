from chocs import HttpCookieJar, HttpCookie
import pytest
from datetime import datetime


def test_can_instantiate():
    jar = HttpCookieJar()
    assert isinstance(jar, HttpCookieJar)


def test_set_simple_cookie():
    jar = HttpCookieJar()
    jar["test"] = "value"

    assert "test" in jar
    assert isinstance(jar["test"], HttpCookie)
    assert "value" == str(jar["test"])


def test_set_cookie():
    jar = HttpCookieJar()
    jar.append(HttpCookie("test", "value"))

    assert "test" in jar
    assert isinstance(jar["test"], HttpCookie)
    assert "value" == str(jar["test"])


def test_override_cookie():
    cookie = HttpCookie("test", "value")
    jar = HttpCookieJar()
    jar["test"] = "value"
    jar.append(cookie)

    assert jar["test"] is cookie

    jar["test"] = "123"
    assert jar["test"] is not cookie


def test_fail_to_change_cookie_name():
    jar = HttpCookieJar()
    jar["test"] = "name"
    cookie = jar["test"]

    with pytest.raises(AttributeError):
        cookie.name = "test-2"


@pytest.mark.parametrize(
    "cookie,expected",
    [
        (HttpCookie("name", "value"), "name=value"),
        (
            HttpCookie("name", "value", expires=datetime(1999, 1, 1)),
            "name=value; Expires=Fri, 01 Jan 1999 00:00:00 ",
        ),
        (HttpCookie("name", "value", http_only=True), "name=value; HttpOnly"),
        (HttpCookie("name", "value", secure=True), "name=value; Secure"),
        (
            HttpCookie("name", "value", secure=True, http_only=True),
            "name=value; Secure; HttpOnly",
        ),
        (
            HttpCookie("name", "value", secure=True, same_site=True),
            "name=value; Secure; SameSite=Strict",
        ),
        (
            HttpCookie(
                "name",
                "value",
                secure=True,
                same_site=True,
                expires=datetime(1999, 1, 1),
            ),
            "name=value; Expires=Fri, 01 Jan 1999 00:00:00 ; Secure; SameSite=Strict",
        ),
    ],
)
def test_serialise_cookie(cookie: HttpCookie, expected: str):
    assert cookie.serialise() == expected


def test_obj_to_json() -> None:
    import json

    obj = {
        "resource": "/test/{id}",
        "path": "/test/123",
        "httpMethod": "GET",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "PL",
            "Cookie": "Cookie_1=value; Cookie_2=value",
            "Host": "aysfy758o4.execute-api.us-east-1.amazonaws.com",
            "Postman-Token": "3b5be8fb-f8ab-4160-981c-eea668b39cab",
            "User-Agent": "PostmanRuntime/7.26.5",
            "Via": "1.1 fb8c0300277bd0137c1693d3d64ab550.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "Cp9vXRHwJ8Nuijbtd5avZDNqU5s9m7lYYptYG4XxJytKQ5-FbKJfhg==",
            "X-Amzn-Trace-Id": "Root=1-5fa80985-120b1d7b015263692774c4c2",
            "X-Forwarded-For": "83.20.81.163, 70.132.1.82",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
        },
        "multiValueHeaders": {
            "Accept": ["*/*"],
            "Accept-Encoding": ["gzip, deflate, br"],
            "CloudFront-Forwarded-Proto": ["https"],
            "CloudFront-Is-Desktop-Viewer": ["true"],
            "CloudFront-Is-Mobile-Viewer": ["false"],
            "CloudFront-Is-SmartTV-Viewer": ["false"],
            "CloudFront-Is-Tablet-Viewer": ["false"],
            "CloudFront-Viewer-Country": ["PL"],
            "Cookie": ["Cookie_1=value; Cookie_2=value"],
            "Host": ["aysfy758o4.execute-api.us-east-1.amazonaws.com"],
            "Postman-Token": ["3b5be8fb-f8ab-4160-981c-eea668b39cab"],
            "User-Agent": ["PostmanRuntime/7.26.5"],
            "Via": ["1.1 fb8c0300277bd0137c1693d3d64ab550.cloudfront.net (CloudFront)"],
            "X-Amz-Cf-Id": ["Cp9vXRHwJ8Nuijbtd5avZDNqU5s9m7lYYptYG4XxJytKQ5-FbKJfhg=="],
            "X-Amzn-Trace-Id": ["Root=1-5fa80985-120b1d7b015263692774c4c2"],
            "X-Forwarded-For": ["83.20.81.163, 70.132.1.82"],
            "X-Forwarded-Port": ["443"],
            "X-Forwarded-Proto": ["https"],
        },
        "queryStringParameters": {
            "query_param[]": "value 3",
            "query_param_2": "value 2",
        },
        "multiValueQueryStringParameters": {
            "query_param[]": ["value", "value 3"],
            "query_param_2": ["value 2"],
        },
        "pathParameters": {"id": "123"},
        "stageVariables": None,
        "requestContext": {
            "resourceId": "jwigqm",
            "resourcePath": "/test/{id}",
            "httpMethod": "GET",
            "extendedRequestId": "VsZszFshIAMFhBw=",
            "requestTime": "08/Nov/2020:15:06:45 +0000",
            "path": "/dev/test/123",
            "accountId": "955411480517",
            "protocol": "HTTP/1.1",
            "stage": "dev",
            "domainPrefix": "aysfy758o4",
            "requestTimeEpoch": 1604848005028,
            "requestId": "1f2ad8c4-0e19-4ff5-9ac6-bdd1bcbf7c0e",
            "identity": {
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": None,
                "sourceIp": "83.20.81.163",
                "principalOrgId": None,
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "PostmanRuntime/7.26.5",
                "user": None,
            },
            "domainName": "aysfy758o4.execute-api.us-east-1.amazonaws.com",
            "apiId": "aysfy758o4",
        },
        "body": None,
        "isBase64Encoded": False,
    }
    stra = json.dumps(obj)
    print(stra)
    a = 1
