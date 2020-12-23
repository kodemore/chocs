from chocs.testing import TestClient
from chocs import Application


class TestTestClient:
    def test_instantiate(self) -> None:
        app = Application()
        client = TestClient(app)

        assert isinstance(client, TestClient)
