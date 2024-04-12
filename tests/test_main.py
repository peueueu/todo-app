from fastapi import status
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}
