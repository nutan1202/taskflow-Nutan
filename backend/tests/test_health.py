from fastapi.testclient import TestClient


def test_health_requires_auth(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 401
    assert r.json() == {"error": "unauthorized"}
