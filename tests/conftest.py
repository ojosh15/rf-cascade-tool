import pytest
from fastapi.testclient import TestClient

from app.register import register_app

app = register_app()

@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client