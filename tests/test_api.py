from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_prompt_too_large(auth_client):

    payload = {
        "prompt": "A" * 6000
    }

    response = auth_client.post(
        "/api/v1/scan",
        json=payload
    )

    assert response.status_code == 422
