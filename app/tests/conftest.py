import pytest
from fastapi.testclient import TestClient

from app.fastapi_app import app

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client