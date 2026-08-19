import pytest
import uuid
from datetime import datetime, UTC, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from database.base import Base
from database.dependencies import get_db
from api.security import get_current_user, create_access_token
from database.models.models import User, Scan, Detection
from database.models.feedback import Feedback, FeedbackLabel
from services.feedback_analytics_service import feedback_analytics_service

@pytest.fixture
def auth_headers(db_session):
    user = User(
        username="analyst_test_18_3",
        email="analyst_test_18_3@example.com",
        hashed_password="hashed_password_123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token(data={"sub": str(user.id)})
    yield {"Authorization": f"Bearer {token}"}, user
    # Cleanup
    db_session.delete(user)
    db_session.commit()

@pytest.fixture
def sample_feedback(db_session, auth_headers):
    _, user = auth_headers
    
    # Create scan 1
    scan1 = Scan(
        prompt="Test prompt 1",
        prompt_length=13,
        risk_score=50,
        severity="medium"
    )
    db_session.add(scan1)
    db_session.commit()
    
    # Create detection 1
    det1 = Detection(
        scan_id=scan1.id,
        technique="DAN",
        detector="semantic",
        severity="medium"
    )
    db_session.add(det1)
    db_session.commit()
    
    # Create feedback 1 (FALSE_POSITIVE)
    fb1 = Feedback(
        scan_id=scan1.id,
        detection_id=det1.id,
        analyst_id=user.id,
        label=FeedbackLabel.FALSE_POSITIVE,
        technique="DAN",
        risk_score=50,
        severity="medium",
        created_at=datetime.now(UTC) - timedelta(days=2)
    )
    db_session.add(fb1)
    
    # Create scan 2
    scan2 = Scan(
        prompt="Test prompt 2",
        prompt_length=13,
        risk_score=90,
        severity="critical"
    )
    db_session.add(scan2)
    db_session.commit()
    
    # Create detection 2
    det2 = Detection(
        scan_id=scan2.id,
        technique="PROMPT_INJECTION",
        detector="regex",
        severity="critical"
    )
    db_session.add(det2)
    db_session.commit()
    
    # Create feedback 2 (CORRECT)
    fb2 = Feedback(
        scan_id=scan2.id,
        detection_id=det2.id,
        analyst_id=user.id,
        label=FeedbackLabel.CORRECT,
        technique="PROMPT_INJECTION",
        risk_score=90,
        severity="critical",
        created_at=datetime.now(UTC) - timedelta(days=1)
    )
    db_session.add(fb2)
    db_session.commit()
    
    yield [fb1, fb2]
    
    # Cleanup
    db_session.delete(fb1)
    db_session.delete(fb2)
    db_session.delete(det1)
    db_session.delete(det2)
    db_session.delete(scan1)
    db_session.delete(scan2)
    db_session.commit()

def test_empty_feedback_database(client, auth_headers, db_session):
    headers, _ = auth_headers
    # clear feedback table safely
    db_session.query(Feedback).delete()
    db_session.commit()
    
    response = client.get("/api/v1/feedback/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_feedback"] == 0
    assert data["correct"] == 0
    assert data["false_positive"] == 0
    assert data["correct_rate"] == 0.0
    assert data["false_positive_rate"] == 0.0

def test_summary_counts(client, auth_headers, sample_feedback):
    headers, _ = auth_headers
    response = client.get("/api/v1/feedback/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_feedback"] == 2
    assert data["correct"] == 1
    assert data["false_positive"] == 1
    assert data["correct_rate"] == 50.0
    assert data["false_positive_rate"] == 50.0

def test_technique_aggregation(client, auth_headers, sample_feedback):
    headers, _ = auth_headers
    response = client.get("/api/v1/feedback/techniques", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "techniques" in data
    assert len(data["techniques"]) == 2
    
    dan = next((t for t in data["techniques"] if t["technique"] == "DAN"), None)
    assert dan is not None
    assert dan["false_positive"] == 1
    assert dan["false_positive_rate"] == 100.0
    
    pi = next((t for t in data["techniques"] if t["technique"] == "PROMPT_INJECTION"), None)
    assert pi is not None
    assert pi["correct"] == 1
    assert pi["correct_rate"] == 100.0 if "correct_rate" in pi else True

def test_detector_aggregation(client, auth_headers, sample_feedback):
    headers, _ = auth_headers
    response = client.get("/api/v1/feedback/detectors", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "detectors" in data
    assert len(data["detectors"]) == 2
    
    semantic = next((d for d in data["detectors"] if d["detector"] == "semantic"), None)
    assert semantic is not None
    assert semantic["false_positive"] == 1

def test_severity_aggregation(client, auth_headers, sample_feedback):
    headers, _ = auth_headers
    response = client.get("/api/v1/feedback/severity", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "severity" in data
    assert len(data["severity"]) == 2

def test_trend_aggregation(client, auth_headers, sample_feedback):
    headers, _ = auth_headers
    response = client.get("/api/v1/feedback/trends?days=7", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["period_days"] == 7
    assert len(data["data"]) == 2 # two different dates

def test_hotspot_detection(client, auth_headers, db_session, sample_feedback):
    headers, _ = auth_headers
    # Sample size is only 1 for each, so with min_sample_size=5, hotspots should be empty
    response = client.get("/api/v1/feedback/hotspots", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["techniques"]) == 0
    
    # Test insights also respects sample size
    response = client.get("/api/v1/feedback/insights", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["insights"]) == 1
    assert data["insights"][0]["confidence"] == "insufficient_sample"

def test_authentication_protection(client):
    response = client.get("/api/v1/feedback/summary")
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main(["-q", __file__])
