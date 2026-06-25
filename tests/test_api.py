from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_prompt_too_large():

    payload = {
        "prompt": "A" * 6000
    }

    response = client.post(
        "/scan",
        json=payload
    )

    assert response.status_code == 422
