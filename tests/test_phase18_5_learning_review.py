import pytest
import uuid
from datetime import datetime, UTC
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from database.models.models import User, Scan, Detection
from database.models.feedback import Feedback, FeedbackLabel
from database.models.learning import LearningCandidate, CandidateStatus, CandidateType, candidate_evidence_table, LearningCandidateReview

@pytest.fixture
def cleanup(db_session):
    db_session.query(LearningCandidateReview).delete()
    db_session.query(LearningCandidate).delete()
    db_session.execute(candidate_evidence_table.delete())
    db_session.query(Feedback).delete()
    db_session.query(Detection).delete()
    db_session.query(Scan).delete()
    db_session.commit()
    
    yield
    
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
        username="analyst_test_18_5",
        email="analyst_test_18_5@example.com",
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

@pytest.fixture
def pending_candidate(db_session, auth_headers, cleanup):
    user = auth_headers[1]
    scan = Scan(prompt="Test prompt", prompt_length=10, risk_score=50, severity="medium")
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
    
    candidate = LearningCandidate(
        candidate_type=CandidateType.TECHNIQUE_REVIEW,
        target="technique",
        technique="DAN",
        sample_size=10,
        false_positive_count=8,
        confidence="HIGH",
        reason="Test candidate",
        status=CandidateStatus.PENDING
    )
    candidate.evidence_feedback.append(fb)
    db_session.add(candidate)
    db_session.commit()
    db_session.refresh(candidate)
    return candidate

def test_approve_candidate(client, auth_headers, db_session, pending_candidate, cleanup):
    headers, user = auth_headers
    
    response = client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        headers=headers,
        json={"decision": "APPROVED", "comment": "Looks good."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["candidate"]["status"] == "APPROVED"
    assert data["review"]["decision"] == "APPROVED"
    assert data["review"]["comment"] == "Looks good."
    assert data["review"]["reviewer_id"] == str(user.id)
    
    # Check persistence
    db_session.expire_all()
    review = db_session.query(LearningCandidateReview).filter(LearningCandidateReview.candidate_id == pending_candidate.id).first()
    assert review is not None
    assert review.decision == CandidateStatus.APPROVED

def test_reject_candidate(client, auth_headers, db_session, pending_candidate, cleanup):
    headers, user = auth_headers
    
    response = client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        headers=headers,
        json={"decision": "REJECTED"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["candidate"]["status"] == "REJECTED"
    assert data["review"]["decision"] == "REJECTED"
    assert data["review"]["comment"] is None

def test_duplicate_review_fails(client, auth_headers, pending_candidate, cleanup):
    headers, user = auth_headers
    
    client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        headers=headers,
        json={"decision": "APPROVED"}
    )
    
    response = client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        headers=headers,
        json={"decision": "REJECTED"}
    )
    
    assert response.status_code == 409
    assert "already APPROVED, cannot review" in response.json()["detail"]

def test_invalid_decision(client, auth_headers, pending_candidate, cleanup):
    headers, user = auth_headers
    
    response = client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        headers=headers,
        json={"decision": "PENDING"} # Invalid decision from PENDING
    )
    
    # Pydantic or our service might catch it. The service catches it as 422 if it makes it past Pydantic.
    # Actually Pydantic will allow it because it's in the CandidateStatus enum.
    assert response.status_code == 422
    assert "Invalid review decision" in response.json()["detail"]

def test_missing_candidate(client, auth_headers):
    headers, _ = auth_headers
    response = client.post(
        f"/api/v1/feedback/learning/candidates/{uuid.uuid4()}/review",
        headers=headers,
        json={"decision": "APPROVED"}
    )
    assert response.status_code == 404

def test_get_review(client, auth_headers, pending_candidate, cleanup):
    headers, user = auth_headers
    
    # Not reviewed yet
    resp1 = client.get(f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review", headers=headers)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["candidate"]["id"] == str(pending_candidate.id)
    assert data1["review"] is None
    
    client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        headers=headers,
        json={"decision": "APPROVED", "comment": "Testing get"}
    )
    
    resp2 = client.get(f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review", headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["review"]["decision"] == "APPROVED"
    assert data2["review"]["comment"] == "Testing get"

def test_auth_protection(client, pending_candidate):
    response = client.post(
        f"/api/v1/feedback/learning/candidates/{pending_candidate.id}/review",
        json={"decision": "APPROVED"}
    )
    assert response.status_code == 401

if __name__ == "__main__":
    pytest.main(["-q", __file__])
