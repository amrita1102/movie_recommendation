from fastapi.testclient import TestClient
from app import app

import pytest


@pytest.fixture
def client():
    return TestClient(app)