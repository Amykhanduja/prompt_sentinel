import pytest
import uuid
from datetime import datetime, UTC, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from database.models.models import User, Scan, Detection
from database.models.feedback import Feedback, FeedbackLabel
from database.models.learning import LearningCandidate, CandidateStatus, CandidateType, candidate_evidence_table, LearningCandidateReview

@pytest.fixture
def cleanup(db_session):
    # Clean up before
    db_session.query(LearningCandidateReview).delete()
    db_session.query(LearningCandidate).delete()
    db_session.execute(candidate_evidence_table.delete())
    db_session.query(Feedback).delete()
    db_session.query(Detection).delete()
    db_session.query(Scan).delete()
    db_session.commit()
    
    yield
    
    # Clean up after
    db_session.query(LearningCandidateReview).delete()
    db_session.query(LearningCandidate).delete()
    db_session.execute(candidate_evidence_table.delete())
    db_session.query(Feedback).delete()
    db_session.query(Detection).delete()
    db_session.query(Scan).delete()
    db_session.commit()

@pytest.fixture
def auth_headers(db_session):
    user = User(
        username="analyst_test_18_4",
        email="analyst_test_18_4@example.com",
        hashed_password="hashed_password_123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    from api.security import create_access_token
    token = create_access_token(data={"sub": str(user.id)})
    yield {"Authorization": f"Bearer {token}"}, user
    
    db_session.delete(user)
    db_session.commit()

def test_generate_no_candidates(client, auth_headers, cleanup):
    headers, _ = auth_headers
    response = client.post("/api/v1/feedback/learning/generate", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_generate_insufficient_sample(client, auth_headers, db_session, cleanup):
    headers, user = auth_headers
    
    # Create 3 FALSE_POSITIVE feedback entries (sample size < 5)
    for i in range(3):
        scan = Scan(prompt=f"Test {i}", prompt_length=10, risk_score=50, severity="medium")
        db_session.add(scan)
        db_session.commit()
        det = Detection(scan_id=scan.id, technique="DAN", detector="semantic", severity="medium")
        db_session.add(det)
        db_session.commit()
        fb = Feedback(
            scan_id=scan.id, detection_id=det.id, analyst_id=user.id,
            label=FeedbackLabel.FALSE_POSITIVE, technique="DAN", risk_score=50, severity="medium"
        )
        db_session.add(fb)
    db_session.commit()
    
    response = client.post("/api/v1/feedback/learning/generate", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0 # insufficient sample should not generate candidates

def test_generate_high_fp_candidates(client, auth_headers, db_session, cleanup):
    headers, user = auth_headers
    
    # Create 5 FALSE_POSITIVE feedback entries (sample size = 5)
    for i in range(5):
        scan = Scan(prompt=f"Test {i}", prompt_length=10, risk_score=50, severity="medium")
        db_session.add(scan)
        db_session.commit()
        det = Detection(scan_id=scan.id, technique="DAN", detector="semantic", severity="medium")
        db_session.add(det)
        db_session.commit()
        fb = Feedback(
            scan_id=scan.id, detection_id=det.id, analyst_id=user.id,
            label=FeedbackLabel.FALSE_POSITIVE, technique="DAN", risk_score=50, severity="medium"
        )
        db_session.add(fb)
    db_session.commit()
    
    response = client.post("/api/v1/feedback/learning/generate", headers=headers)
    assert response.status_code == 200
    candidates = response.json()
    assert len(candidates) > 0
    
    # Check that we have a technique review candidate for DAN
    tech_cand = next((c for c in candidates if c["candidate_type"] == "TECHNIQUE_REVIEW" and c["technique"] == "DAN"), None)
    assert tech_cand is not None
    assert tech_cand["status"] == "PENDING"
    assert tech_cand["sample_size"] == 5
    assert tech_cand["false_positive_count"] == 5
    assert tech_cand["confidence"] != "INSUFFICIENT"
    
    # Check that we have a threshold adjustment candidate for semantic
    det_cand = next((c for c in candidates if c["candidate_type"] == "THRESHOLD_ADJUSTMENT" and c["detector"] == "semantic"), None)
    assert det_cand is not None
    assert det_cand["status"] == "PENDING"
    assert det_cand["current_value"] is not None
    assert det_cand["proposed_value"] is not None
    assert det_cand["proposed_value"] > det_cand["current_value"]
    
def test_deduplication(client, auth_headers, db_session, cleanup):
    headers, user = auth_headers
    
    # Create 5 FALSE_POSITIVE feedback entries (sample size = 5)
    for i in range(5):
        scan = Scan(prompt=f"Test {i}", prompt_length=10, risk_score=50, severity="medium")
        db_session.add(scan)
        db_session.commit()
        det = Detection(scan_id=scan.id, technique="DAN", detector="semantic", severity="medium")
        db_session.add(det)
        db_session.commit()
        fb = Feedback(
            scan_id=scan.id, detection_id=det.id, analyst_id=user.id,
            label=FeedbackLabel.FALSE_POSITIVE, technique="DAN", risk_score=50, severity="medium"
        )
        db_session.add(fb)
    db_session.commit()
    
    # First generation
    resp1 = client.post("/api/v1/feedback/learning/generate", headers=headers)
    c1 = len(resp1.json())
    
    # Second generation should not duplicate
    resp2 = client.post("/api/v1/feedback/learning/generate", headers=headers)
    c2 = len(resp2.json())
    
    assert c1 == c2

def test_candidate_details_and_evidence(client, auth_headers, db_session, cleanup):
    headers, user = auth_headers
    
    # Create 5 FALSE_POSITIVE feedback entries (sample size = 5)
    fb_ids = []
    for i in range(5):
        scan = Scan(prompt=f"Test {i}", prompt_length=10, risk_score=50, severity="medium")
        db_session.add(scan)
        db_session.commit()
        det = Detection(scan_id=scan.id, technique="DAN", detector="semantic", severity="medium")
        db_session.add(det)
        db_session.commit()
        fb = Feedback(
            scan_id=scan.id, detection_id=det.id, analyst_id=user.id,
            label=FeedbackLabel.FALSE_POSITIVE, technique="DAN", risk_score=50, severity="medium"
        )
        db_session.add(fb)
        db_session.commit()
        fb_ids.append(str(fb.id))
        
    resp1 = client.post("/api/v1/feedback/learning/generate", headers=headers)
    candidates = resp1.json()
    assert len(candidates) > 0
    
    cand_id = candidates[0]["id"]
    
    # Get details
    resp_det = client.get(f"/api/v1/feedback/learning/candidates/{cand_id}", headers=headers)
    assert resp_det.status_code == 200
    cand_detail = resp_det.json()
    
    assert cand_detail["id"] == cand_id
    assert "evidence_feedback_ids" in cand_detail
    assert len(cand_detail["evidence_feedback_ids"]) == 5
    # Just check if our generated fb_ids are in the list
    for f_id in cand_detail["evidence_feedback_ids"]:
        assert str(f_id) in fb_ids

def test_authentication_protection(client):
    response = client.post("/api/v1/feedback/learning/generate")
    assert response.status_code == 401
    
    response = client.get("/api/v1/feedback/learning/candidates")
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main(["-q", __file__])
