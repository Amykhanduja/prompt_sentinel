import pytest
import uuid
from sqlalchemy.exc import IntegrityError
from database.models.models import User, Scan, Detection
from database.models.feedback import Feedback, FeedbackLabel
from database.repositories.feedback_repository import feedback_repository
from services.feedback_service import feedback_service

@pytest.fixture(scope="function")
def cleanup(db_session):
    yield
    db_session.execute(Feedback.__table__.delete())
    db_session.execute(Detection.__table__.delete())
    db_session.execute(Scan.__table__.delete())
    db_session.execute(User.__table__.delete())
    db_session.commit()

@pytest.fixture
def analyst(db_session):
    user = User(
        username=f"analyst_{uuid.uuid4()}", 
        email=f"{uuid.uuid4()}@example.com", 
        hashed_password="hash"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def scan_with_detection(db_session):
    scan = Scan(
        prompt="Test prompt",
        prompt_length=11,
        risk_score=75,
        preprocessing_flags={"transformations": ["WHITESPACE_NORMALIZED"]},
        risk_summary={"obfuscated": True}
    )
    db_session.add(scan)
    db_session.commit()
    
    detection = Detection(
        scan_id=scan.id,
        technique="Prompt Injection",
        severity="high"
    )
    db_session.add(detection)
    db_session.commit()
    db_session.refresh(scan)
    db_session.refresh(detection)
    return scan, detection

def test_feedback_creation_and_retrieval(db_session, analyst, scan_with_detection, cleanup):
    scan, detection = scan_with_detection
    
    feedback = feedback_service.create_feedback(
        db_session,
        analyst_id=analyst.id,
        detection_id=detection.id,
        label_str="CORRECT"
    )
    
    assert feedback.id is not None
    assert feedback.label == FeedbackLabel.CORRECT
    
    retrieved = feedback_repository.get_by_id(db_session, feedback.id)
    assert retrieved is not None
    assert retrieved.id == feedback.id

def test_feedback_labels(db_session, analyst, scan_with_detection, cleanup):
    scan, detection = scan_with_detection
    
    # CORRECT
    fb1 = feedback_service.create_feedback(
        db_session, analyst_id=analyst.id, detection_id=detection.id, label_str="CORRECT"
    )
    assert fb1.label == FeedbackLabel.CORRECT
    
    # FALSE_POSITIVE
    detection2 = Detection(scan_id=scan.id, technique="Another", severity="low")
    db_session.add(detection2)
    db_session.commit()
    
    fb2 = feedback_service.create_feedback(
        db_session, analyst_id=analyst.id, detection_id=detection2.id, label_str="FALSE_POSITIVE"
    )
    assert fb2.label == FeedbackLabel.FALSE_POSITIVE

def test_invalid_label_rejected(db_session, analyst, scan_with_detection, cleanup):
    scan, detection = scan_with_detection
    with pytest.raises(ValueError, match="Invalid feedback label"):
        feedback_service.create_feedback(
            db_session, analyst_id=analyst.id, detection_id=detection.id, label_str="INVALID_LABEL"
        )

def test_feedback_preserves_context(db_session, analyst, scan_with_detection, cleanup):
    scan, detection = scan_with_detection
    
    feedback = feedback_service.create_feedback(
        db_session, analyst_id=analyst.id, detection_id=detection.id, label_str="CORRECT"
    )
    
    assert feedback.analyst_id == analyst.id
    assert feedback.scan_id == scan.id
    assert feedback.detection_id == detection.id
    assert feedback.technique == "Prompt Injection"
    assert feedback.risk_score == 75
    assert feedback.severity == "high"
    assert feedback.transformations == ["WHITESPACE_NORMALIZED"]
    assert feedback.obfuscation_detected is True
    assert feedback.created_at is not None

def test_duplicate_feedback_prevented(db_session, analyst, scan_with_detection, cleanup):
    scan, detection = scan_with_detection
    
    feedback_service.create_feedback(
        db_session, analyst_id=analyst.id, detection_id=detection.id, label_str="CORRECT"
    )
    
    with pytest.raises(IntegrityError):
        feedback_service.create_feedback(
            db_session, analyst_id=analyst.id, detection_id=detection.id, label_str="FALSE_POSITIVE"
        )
    db_session.rollback()

def test_multiple_detections_independent_feedback(db_session, analyst, scan_with_detection, cleanup):
    scan, detection1 = scan_with_detection
    
    detection2 = Detection(scan_id=scan.id, technique="Second", severity="low")
    db_session.add(detection2)
    db_session.commit()
    
    fb1 = feedback_service.create_feedback(
        db_session, analyst_id=analyst.id, detection_id=detection1.id, label_str="CORRECT"
    )
    fb2 = feedback_service.create_feedback(
        db_session, analyst_id=analyst.id, detection_id=detection2.id, label_str="FALSE_POSITIVE"
    )
    
    assert fb1.id != fb2.id
    assert fb1.detection_id == detection1.id
    assert fb2.detection_id == detection2.id
