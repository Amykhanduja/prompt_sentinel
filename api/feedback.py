import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.dependencies import get_db
from database.models.models import User
from api.security import get_current_user
from services.feedback_service import feedback_service
from database.repositories.feedback_repository import feedback_repository

router = APIRouter()

class FeedbackCreateRequest(BaseModel):
    detection_id: uuid.UUID
    label: str
    
    model_config = ConfigDict(extra="forbid")

class FeedbackResponse(BaseModel):
    id: uuid.UUID
    detection_id: uuid.UUID
    label: str
    technique: Optional[str] = None
    risk_score: int
    severity: str
    transformations: Optional[list] = None
    obfuscation_detected: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    request: FeedbackCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        feedback = feedback_service.create_feedback(
            db=db,
            analyst_id=current_user.id,
            detection_id=request.detection_id,
            label_str=request.label
        )
        return feedback
    except ValueError as e:
        error_msg = str(e)
        if "Invalid feedback label" in error_msg:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_msg)
        elif "Detection" in error_msg and "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        elif "Scan for detection" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Feedback already submitted for this detection"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/detection/{detection_id}", response_model=List[FeedbackResponse])
def get_feedback_for_detection(
    detection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_repository.get_by_detection_id(db, detection_id)

@router.get("/me", response_model=List[FeedbackResponse])
def get_current_analyst_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_repository.get_by_analyst_id(db, current_user.id)

# ==========================================
# PHASE 18.3 ANALYTICS ENDPOINTS
# ==========================================

from services.feedback_analytics_service import feedback_analytics_service
from fastapi import Query

class FeedbackSummaryResponse(BaseModel):
    total_feedback: int
    correct: int
    false_positive: int
    false_negative: int
    correct_rate: float
    false_positive_rate: float
    false_negative_rate: float

class TechniqueStats(BaseModel):
    technique: str
    total: int
    correct: int
    false_positive: int
    false_negative: int
    false_positive_rate: float
    false_negative_rate: float

class FeedbackTechniqueResponse(BaseModel):
    techniques: List[TechniqueStats]

class DetectorStats(BaseModel):
    detector: str
    total: int
    correct: int
    false_positive: int
    false_negative: int
    false_positive_rate: float

class FeedbackDetectorResponse(BaseModel):
    detectors: List[DetectorStats]

class SeverityStats(BaseModel):
    severity: str
    total: int
    correct: int
    false_positive: int
    false_negative: int

class FeedbackSeverityResponse(BaseModel):
    severity: List[SeverityStats]

class TrendData(BaseModel):
    date: str
    total: int
    correct: int
    false_positive: int
    false_negative: int

class FeedbackTrendResponse(BaseModel):
    period_days: int
    data: List[TrendData]

class HotspotTechnique(BaseModel):
    technique: str
    total: int
    false_positive: int
    false_positive_rate: float

class FeedbackHotspotsResponse(BaseModel):
    techniques: List[HotspotTechnique]

class InsightItem(BaseModel):
    type: Optional[str] = None
    detector: Optional[str] = None
    technique: Optional[str] = None
    false_positive_rate: Optional[float] = None
    sample_size: Optional[int] = None
    message: Optional[str] = None
    confidence: Optional[str] = None

class FeedbackInsightsResponse(BaseModel):
    insights: List[InsightItem]

@router.get("/summary", response_model=FeedbackSummaryResponse)
def get_feedback_summary_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.get_feedback_summary(db)

@router.get("/techniques", response_model=FeedbackTechniqueResponse)
def get_feedback_techniques_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.get_feedback_by_technique(db)

@router.get("/detectors", response_model=FeedbackDetectorResponse)
def get_feedback_detectors_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.get_feedback_by_detector(db)

@router.get("/severity", response_model=FeedbackSeverityResponse)
def get_feedback_severity_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.get_feedback_by_severity(db)

@router.get("/trends", response_model=FeedbackTrendResponse)
def get_feedback_trends_api(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.get_feedback_trends(db, days)

@router.get("/hotspots", response_model=FeedbackHotspotsResponse)
def get_feedback_hotspots_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.get_feedback_hotspots(db)

@router.get("/insights", response_model=FeedbackInsightsResponse)
def get_feedback_insights_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_analytics_service.generate_feedback_insights(db)

# ==========================================
# PHASE 18.4 LEARNING CANDIDATE ENDPOINTS
# ==========================================

from database.models.learning import CandidateType, CandidateStatus, CandidateConfidence
from services.feedback_learning_service import feedback_learning_service

class LearningCandidateResponse(BaseModel):
    id: uuid.UUID
    candidate_type: CandidateType
    target: str
    technique: Optional[str] = None
    detector: Optional[str] = None
    current_value: Optional[float] = None
    proposed_value: Optional[float] = None
    sample_size: int
    false_positive_count: int
    false_negative_count: int
    confidence: CandidateConfidence
    reason: str
    status: CandidateStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LearningCandidateDetailResponse(LearningCandidateResponse):
    evidence_feedback_ids: List[uuid.UUID]

    model_config = ConfigDict(from_attributes=True)

@router.post("/learning/generate", response_model=List[LearningCandidateResponse])
def generate_learning_candidates_api(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger candidate analysis and generation. 
    Reads feedback analytics and identifies statistically meaningful patterns.
    Does NOT apply changes.
    """
    return feedback_learning_service.generate_learning_candidates(db)

@router.get("/learning/candidates", response_model=List[LearningCandidateResponse])
def get_learning_candidates_api(
    status: Optional[CandidateStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return feedback_learning_service.get_candidates(db, status=status)

@router.get("/learning/candidates/{candidate_id}", response_model=LearningCandidateDetailResponse)
def get_learning_candidate_detail_api(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    candidate = feedback_learning_service.get_candidate(db, str(candidate_id))
    if not candidate:
        raise HTTPException(status_code=404, detail="Learning candidate not found")
        
    # Map evidence IDs manually to avoid exposing full feedback rows
    evidence_ids = [fb.id for fb in candidate.evidence_feedback]
    
    response = LearningCandidateDetailResponse(
        id=candidate.id,
        candidate_type=candidate.candidate_type,
        target=candidate.target,
        technique=candidate.technique,
        detector=candidate.detector,
        current_value=candidate.current_value,
        proposed_value=candidate.proposed_value,
        sample_size=candidate.sample_size,
        false_positive_count=candidate.false_positive_count,
        false_negative_count=candidate.false_negative_count,
        confidence=candidate.confidence,
        reason=candidate.reason,
        status=candidate.status,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        evidence_feedback_ids=evidence_ids
    )
    return response

# ==========================================
# PHASE 18.5 LEARNING CANDIDATE REVIEW ENDPOINTS
# ==========================================

from services.feedback_review_service import feedback_review_service

class LearningCandidateReviewRequest(BaseModel):
    decision: CandidateStatus
    comment: Optional[str] = None
    
    model_config = ConfigDict(extra="forbid")

class LearningCandidateReviewResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    reviewer_id: uuid.UUID
    decision: CandidateStatus
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LearningCandidateReviewDetailResponse(BaseModel):
    candidate: LearningCandidateDetailResponse
    review: Optional[LearningCandidateReviewResponse] = None

@router.post("/learning/candidates/{candidate_id}/review", response_model=LearningCandidateReviewDetailResponse)
def review_learning_candidate_api(
    candidate_id: uuid.UUID,
    request: LearningCandidateReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        candidate = feedback_review_service.review_candidate(
            db=db,
            candidate_id=str(candidate_id),
            reviewer_id=current_user.id,
            decision=request.decision,
            comment=request.comment
        )
        
        review = feedback_review_service.get_candidate_review(db, str(candidate_id))
        
        evidence_ids = [fb.id for fb in candidate.evidence_feedback]
        candidate_resp = LearningCandidateDetailResponse(
            id=candidate.id,
            candidate_type=candidate.candidate_type,
            target=candidate.target,
            technique=candidate.technique,
            detector=candidate.detector,
            current_value=candidate.current_value,
            proposed_value=candidate.proposed_value,
            sample_size=candidate.sample_size,
            false_positive_count=candidate.false_positive_count,
            false_negative_count=candidate.false_negative_count,
            confidence=candidate.confidence,
            reason=candidate.reason,
            status=candidate.status,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            evidence_feedback_ids=evidence_ids
        )
        
        return LearningCandidateReviewDetailResponse(
            candidate=candidate_resp,
            review=LearningCandidateReviewResponse.model_validate(review) if review else None
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "already" in error_msg and "cannot review" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        elif "A review already exists" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=422, detail=error_msg)

@router.get("/learning/candidates/{candidate_id}/review", response_model=LearningCandidateReviewDetailResponse)
def get_learning_candidate_review_api(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    candidate = feedback_learning_service.get_candidate(db, str(candidate_id))
    if not candidate:
        raise HTTPException(status_code=404, detail="Learning candidate not found")
        
    review = feedback_review_service.get_candidate_review(db, str(candidate_id))
    
    evidence_ids = [fb.id for fb in candidate.evidence_feedback]
    candidate_resp = LearningCandidateDetailResponse(
        id=candidate.id,
        candidate_type=candidate.candidate_type,
        target=candidate.target,
        technique=candidate.technique,
        detector=candidate.detector,
        current_value=candidate.current_value,
        proposed_value=candidate.proposed_value,
        sample_size=candidate.sample_size,
        false_positive_count=candidate.false_positive_count,
        false_negative_count=candidate.false_negative_count,
        confidence=candidate.confidence,
        reason=candidate.reason,
        status=candidate.status,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
        evidence_feedback_ids=evidence_ids
    )
    
    return LearningCandidateReviewDetailResponse(
        candidate=candidate_resp,
        review=LearningCandidateReviewResponse.model_validate(review) if review else None
    )

# ==========================================
# PHASE 18.6 LEARNING APPLICATION ENDPOINTS
# ==========================================

from database.models.learning import ApplicationStatus
from services.learning_application_service import learning_application_service

class LearningApplicationResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    config_id: uuid.UUID
    applied_by: uuid.UUID
    version: int
    change_type: str
    target: str
    previous_value: Optional[float] = None
    new_value: float
    status: ApplicationStatus
    created_at: datetime
    activated_at: datetime
    rolled_back_at: Optional[datetime] = None
    rollback_reason: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class RollbackRequest(BaseModel):
    reason: str
    
    model_config = ConfigDict(extra="forbid")

@router.post("/learning/candidates/{candidate_id}/apply", response_model=LearningApplicationResponse)
def apply_learning_candidate_api(
    candidate_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        application = learning_application_service.apply_candidate(
            db=db,
            candidate_id=str(candidate_id),
            applied_by=current_user.id
        )
        return application
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "PENDING" in error_msg or "REJECTED" in error_msg or "already been applied" in error_msg or "Duplicate" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        elif "Unsupported candidate type" in error_msg or "Proposed value must be between" in error_msg:
            raise HTTPException(status_code=422, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

@router.post("/learning/applications/{application_id}/rollback", response_model=LearningApplicationResponse)
def rollback_learning_application_api(
    application_id: uuid.UUID,
    request: RollbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        application = learning_application_service.rollback_application(
            db=db,
            application_id=str(application_id),
            reason=request.reason
        )
        return application
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "already rolled back" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)

@router.get("/learning/applications", response_model=List[LearningApplicationResponse])
def get_learning_applications_api(
    status: Optional[ApplicationStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return learning_application_service.get_applications(db, status=status)

@router.get("/learning/applications/{application_id}", response_model=LearningApplicationResponse)
def get_learning_application_detail_api(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    application = learning_application_service.get_application(db, str(application_id))
    if not application:
        raise HTTPException(status_code=404, detail="Learning application not found")
    return application

