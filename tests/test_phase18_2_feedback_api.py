import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from database.models.models import User, Scan, Detection
from database.models.feedback import Feedback
from app import app
from api.security import create_access_token

@pytest.fixture(scope="function")
def cleanup(db_session):
    yield
    db_session.execute(Feedback.__table__.delete())
    db_session.execute(Detection.__table__.delete())
    db_session.execute(Scan.__table__.delete())
    db_session.execute(User.__table__.delete())
    db_session.commit()

@pytest.fixture
def auth_user(db_session):
    user = User(
        username=f"analyst_{uuid.uuid4()}", 
        email=f"{uuid.uuid4()}@example.com", 
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id)})
    return user, {"Authorization": f"Bearer {token}"}

@pytest.fixture
def another_auth_user(db_session):
    user = User(
        username=f"analyst_2_{uuid.uuid4()}", 
        email=f"{uuid.uuid4()}@example.com", 
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id)})
    return user, {"Authorization": f"Bearer {token}"}

@pytest.fixture
def scan_detection(db_session):
    scan = Scan(
        prompt="Test prompt",
        prompt_length=11,
        risk_score=82,
        preprocessing_flags={"transformations": ["LEETSPEAK_NORMALIZED"]},
        risk_summary={"obfuscated": True}
    )
    db_session.add(scan)
    db_session.commit()
    
    detection = Detection(
        scan_id=scan.id,
        technique="PT-001",
        severity="high"
    )
    db_session.add(detection)
    db_session.commit()
    db_session.refresh(scan)
    db_session.refresh(detection)
    return scan, detection

def test_post_feedback_unauthenticated(client, scan_detection):
    scan, detection = scan_detection
    response = client.post("/api/v1/feedback/", json={
        "detection_id": str(detection.id),
        "label": "CORRECT"
    })
    assert response.status_code == 401

def test_post_feedback_authenticated_correct(client, auth_user, scan_detection, cleanup):
    _, headers = auth_user
    scan, detection = scan_detection
    
    response = client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(detection.id),
        "label": "CORRECT"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["label"] == "CORRECT"
    assert data["technique"] == "PT-001"
    assert data["risk_score"] == 82
    assert data["severity"] == "high"
    assert data["transformations"] == ["LEETSPEAK_NORMALIZED"]
    assert data["obfuscation_detected"] is True

def test_post_feedback_authenticated_false_positive(client, auth_user, scan_detection, cleanup):
    _, headers = auth_user
    scan, detection = scan_detection
    
    response = client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(detection.id),
        "label": "FALSE_POSITIVE"
    })
    assert response.status_code == 201
    assert response.json()["label"] == "FALSE_POSITIVE"

def test_post_feedback_invalid_label(client, auth_user, scan_detection, cleanup):
    _, headers = auth_user
    scan, detection = scan_detection
    
    response = client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(detection.id),
        "label": "MAYBE"
    })
    assert response.status_code == 422

def test_post_feedback_missing_detection(client, auth_user, cleanup):
    _, headers = auth_user
    
    response = client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(uuid.uuid4()),
        "label": "CORRECT"
    })
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_post_feedback_duplicate_returns_409(client, auth_user, scan_detection, cleanup):
    _, headers = auth_user
    scan, detection = scan_detection
    
    client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(detection.id),
        "label": "CORRECT"
    })
    
    response = client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(detection.id),
        "label": "FALSE_POSITIVE"
    })
    assert response.status_code == 409

def test_post_feedback_forbids_extra_fields(client, auth_user, scan_detection, cleanup):
    _, headers = auth_user
    scan, detection = scan_detection
    
    response = client.post("/api/v1/feedback/", headers=headers, json={
        "detection_id": str(detection.id),
        "label": "CORRECT",
        "analyst_id": str(uuid.uuid4()),
        "risk_score": 99
    })
    # Pydantic ConfigDict(extra="forbid") should catch this
    assert response.status_code == 422

def test_get_feedback_for_detection(client, auth_user, another_auth_user, scan_detection, cleanup):
    _, headers1 = auth_user
    _, headers2 = another_auth_user
    scan, detection = scan_detection
    
    client.post("/api/v1/feedback/", headers=headers1, json={
        "detection_id": str(detection.id),
        "label": "CORRECT"
    })
    
    client.post("/api/v1/feedback/", headers=headers2, json={
        "detection_id": str(detection.id),
        "label": "FALSE_POSITIVE"
    })
    
    response = client.get(f"/api/v1/feedback/detection/{detection.id}", headers=headers1)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_feedback_me(client, auth_user, another_auth_user, scan_detection, cleanup, db_session):
    user1, headers1 = auth_user
    user2, headers2 = another_auth_user
    scan, detection = scan_detection
    
    # Give user 2 a detection as well
    detection2 = Detection(scan_id=scan.id, technique="PT-002", severity="low")
    
    db_session.add(detection2)
    db_session.commit()
    db_session.refresh(detection2)
    
    client.post("/api/v1/feedback/", headers=headers1, json={
        "detection_id": str(detection.id),
        "label": "CORRECT"
    })
    
    client.post("/api/v1/feedback/", headers=headers2, json={
        "detection_id": str(detection2.id),
        "label": "FALSE_POSITIVE"
    })
    
    # user1 /me should return 1 feedback for user1
    response = client.get("/api/v1/feedback/me", headers=headers1)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["label"] == "CORRECT"
    
    
