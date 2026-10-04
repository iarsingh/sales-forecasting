from fastapi.testclient import TestClient
from salesfc.main import app

client = TestClient(app)


def test_moving_average():
    payload = client.post("/forecast", json={"series": [10, 20, 30, 40]}).json()
    assert payload["next"] == 30.0


def test_short_series_is_refused():
    assert client.post("/forecast", json={"series": [1]}).status_code == 422
