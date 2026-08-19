import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from database.models.learning import (
    LearningCandidate, CandidateType, CandidateStatus, CandidateConfidence,
    LearningApplication, ApplicationStatus, LearningConfig, LearningRule
)
from database.models.models import User
from semantic.semantic_engine import _ENGINE
from config import DEFAULT_SIMILARITY_THRESHOLD
from services.learning_configuration_service import learning_configuration_service
from services.learning_application_service import learning_application_service

def test_cannot_apply_pending_candidate(db_session):
    user = User(username="admin", hashed_password="hash", role="admin")
    db_session.add(user)
    db_session.commit()
    
    candidate = LearningCandidate(
        candidate_type=CandidateType.THRESHOLD_ADJUSTMENT,
        target="semantic",
        current_value=0.75,
        proposed_value=0.85,
        confidence=CandidateConfidence.HIGH,
        reason="Test",
        status=CandidateStatus.PENDING
    )
    db_session.add(candidate)
    db_session.commit()
    
    with pytest.raises(ValueError, match="Cannot apply a PENDING candidate"):
        learning_application_service.apply_candidate(db_session, str(candidate.id), user.id)

def test_cannot_apply_rejected_candidate(db_session):
    user = User(username="admin", hashed_password="hash", role="admin")
    db_session.add(user)
    db_session.commit()
    
    candidate = LearningCandidate(
        candidate_type=CandidateType.THRESHOLD_ADJUSTMENT,
        target="semantic",
        current_value=0.75,
        proposed_value=0.85,
        confidence=CandidateConfidence.HIGH,
        reason="Test",
        status=CandidateStatus.REJECTED
    )
    db_session.add(candidate)
    db_session.commit()
    
    with pytest.raises(ValueError, match="Cannot apply a REJECTED candidate"):
        learning_application_service.apply_candidate(db_session, str(candidate.id), user.id)

def test_apply_approved_candidate(db_session):
    user = User(username="admin", hashed_password="hash", role="admin")
    db_session.add(user)
    db_session.commit()
    
    candidate = LearningCandidate(
        candidate_type=CandidateType.THRESHOLD_ADJUSTMENT,
        target="semantic",
        current_value=0.75,
        proposed_value=0.85,
        confidence=CandidateConfidence.HIGH,
        reason="Test",
        status=CandidateStatus.APPROVED
    )
    db_session.add(candidate)
    db_session.commit()
    
    app = learning_application_service.apply_candidate(db_session, str(candidate.id), user.id)
    
    assert app.status == ApplicationStatus.APPLIED
    assert app.new_value == 0.85
    assert app.version == 1
    
    # Check config
    config = learning_configuration_service.get_active_learning_config(db_session)
    assert config.get("semantic") == 0.85
    
def test_rollback_application(db_session):
    user = User(username="admin", hashed_password="hash", role="admin")
    db_session.add(user)
    db_session.commit()
    
    candidate = LearningCandidate(
        candidate_type=CandidateType.THRESHOLD_ADJUSTMENT,
        target="semantic",
        current_value=0.75,
        proposed_value=0.85,
        confidence=CandidateConfidence.HIGH,
        reason="Test",
        status=CandidateStatus.APPROVED
    )
    db_session.add(candidate)
    db_session.commit()
    
    app = learning_application_service.apply_candidate(db_session, str(candidate.id), user.id)
    assert learning_configuration_service.get_active_learning_config(db_session).get("semantic") == 0.85
    
    learning_application_service.rollback_application(db_session, str(app.id), "Didn't work out")
    
    # Check config after rollback
    config = learning_configuration_service.get_active_learning_config(db_session)
    assert "semantic" not in config

def test_detect_semantic_uses_learned_config(db_session):
    from detectors.engine import run_detectors
    
    # Baseline detect
    baseline_result = run_detectors("This is a semantic test prompt")
    
    # Let's mock the active config in db
    user = User(username="admin", hashed_password="hash", role="admin")
    db_session.add(user)
    
    candidate = LearningCandidate(
        candidate_type=CandidateType.THRESHOLD_ADJUSTMENT,
        target="semantic",
        current_value=0.75,
        proposed_value=0.99, # Very high threshold, should block everything
        confidence=CandidateConfidence.HIGH,
        reason="Test",
        status=CandidateStatus.APPROVED
    )
    db_session.add(candidate)
    db_session.commit()
    
    learning_application_service.apply_candidate(db_session, str(candidate.id), user.id)
    
    # We must ensure the new active config is visible to the pipeline.
    # We will invoke detect_semantic directly to confirm.
    from semantic.semantic_engine import detect_semantic
    active_config = learning_configuration_service.get_active_learning_config(db_session)
    result = detect_semantic("This is a semantic test prompt", active_config=active_config)
    assert len(result) == 0 or all(r['similarity'] >= 0.99 for r in result)

