from chocs import Application, HttpStatus
from chocs.testing import TestClient
from tests.fixtures.app_fixture import app

app.use("tests.fixtures.routes_fixture")
TestClient.__test__ = False


class TestTestClient:
    def test_instantiate(self) -> None:
        client = TestClient(Application())

        assert isinstance(client, TestClient)

    def test_get(self) -> None:
        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == HttpStatus.OK
        assert response.as_str() == "test get"

    def test_post(self) -> None:
        client = TestClient(app)
        response = client.post("/test")
        assert response.status_code == HttpStatus.OK
        assert response.as_str() == "test post"

    def test_patch(self) -> None:
        client = TestClient(app)
        response = client.patch("/test")
        assert response.status_code == HttpStatus.OK
        assert response.as_str() == "test patch"

    def test_delete(self) -> None:
        client = TestClient(app)
        response = client.delete("/test")
        assert response.status_code == HttpStatus.OK
        assert response.as_str() == "test delete"

    def test_options(self) -> None:
        client = TestClient(app)
        response = client.options("/test")
        assert response.status_code == HttpStatus.OK
        assert response.as_str() == "test options"

    def test_head(self) -> None:
        client = TestClient(app)
        response = client.head("/test")
        assert response.status_code == HttpStatus.OK
        assert response.as_str() == "test head"
