from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_scan_markdown_file():

    with open("tests/sample.md", "rb") as file:

        response = client.post(
            "/api/v1/scan-file",
            files={
                "file": (
                    "sample.md",
                    file,
                    "text/markdown"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert "detections" in data
    assert "risk_score" in data
    assert "action" in data
