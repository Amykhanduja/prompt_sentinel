from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional

from database.models.learning import LearningCandidate, CandidateType, CandidateStatus, CandidateConfidence
from database.models.feedback import Feedback, FeedbackLabel
from database.models.models import Detection
from services.feedback_analytics_service import feedback_analytics_service
import config

class FeedbackLearningService:
    def _calculate_confidence(self, sample_size: int, fp_rate: float) -> CandidateConfidence:
        if sample_size < 5:
            return CandidateConfidence.INSUFFICIENT
        if sample_size >= 20 and fp_rate > 50.0:
            return CandidateConfidence.HIGH
        if sample_size >= 10 and fp_rate > 35.0:
            return CandidateConfidence.MEDIUM
        return CandidateConfidence.LOW

    def _get_evidence_for_technique(self, db: Session, technique: str) -> List[Feedback]:
        return db.query(Feedback).filter(
            Feedback.technique == technique,
            Feedback.label == FeedbackLabel.FALSE_POSITIVE
        ).all()
        
    def _get_evidence_for_detector(self, db: Session, detector: str) -> List[Feedback]:
        return db.query(Feedback).join(Detection, Feedback.detection_id == Detection.id).filter(
            Detection.detector == detector,
            Feedback.label == FeedbackLabel.FALSE_POSITIVE
        ).all()

    def generate_learning_candidates(self, db: Session) -> List[LearningCandidate]:
        candidates = []
        
        # 1. Technique-based candidates
        tech_data = feedback_analytics_service.get_feedback_by_technique(db)
        for t in tech_data["techniques"]:
            if t["total"] >= 5 and t["false_positive_rate"] > 20.0:
                confidence = self._calculate_confidence(t["total"], t["false_positive_rate"])
                if confidence != CandidateConfidence.INSUFFICIENT:
                    # Check deduplication
                    existing = db.query(LearningCandidate).filter(
                        LearningCandidate.candidate_type == CandidateType.TECHNIQUE_REVIEW,
                        LearningCandidate.technique == t["technique"],
                        LearningCandidate.status == CandidateStatus.PENDING
                    ).first()
                    
                    if not existing:
                        candidate = LearningCandidate(
                            candidate_type=CandidateType.TECHNIQUE_REVIEW,
                            target="technique",
                            technique=t["technique"],
                            detector=None,
                            sample_size=t["total"],
                            false_positive_count=t["false_positive"],
                            confidence=confidence,
                            reason=f"High false-positive rate ({t['false_positive_rate']}%) for technique {t['technique']}"
                        )
                        # Add evidence
                        evidence = self._get_evidence_for_technique(db, t["technique"])
                        candidate.evidence_feedback.extend(evidence)
                        
                        db.add(candidate)
                        candidates.append(candidate)

        # 2. Detector-based threshold adjustment candidates
        det_data = feedback_analytics_service.get_feedback_by_detector(db)
        for d in det_data["detectors"]:
            if d["total"] >= 5 and d["false_positive_rate"] > 25.0:
                confidence = self._calculate_confidence(d["total"], d["false_positive_rate"])
                if confidence != CandidateConfidence.INSUFFICIENT:
                    # Check deduplication
                    existing = db.query(LearningCandidate).filter(
                        LearningCandidate.candidate_type == CandidateType.THRESHOLD_ADJUSTMENT,
                        LearningCandidate.detector == d["detector"],
                        LearningCandidate.status == CandidateStatus.PENDING
                    ).first()
                    
                    if not existing:
                        current_val = None
                        proposed_val = None
                        if d["detector"] == "semantic":
                            current_val = getattr(config, "DEFAULT_SIMILARITY_THRESHOLD", 0.75)
                            # Bounded proposed value, slightly higher to reduce false positives
                            proposed_val = min(0.99, round(current_val + 0.05, 2))
                            
                        candidate = LearningCandidate(
                            candidate_type=CandidateType.THRESHOLD_ADJUSTMENT,
                            target=d["detector"],
                            detector=d["detector"],
                            current_value=current_val,
                            proposed_value=proposed_val,
                            sample_size=d["total"],
                            false_positive_count=d["false_positive"],
                            confidence=confidence,
                            reason=f"Detector '{d['detector']}' has a high false-positive rate ({d['false_positive_rate']}%). Recommend threshold adjustment."
                        )
                        # Add evidence
                        evidence = self._get_evidence_for_detector(db, d["detector"])
                        candidate.evidence_feedback.extend(evidence)
                        
                        db.add(candidate)
                        candidates.append(candidate)
                        
        db.commit()
        for c in candidates:
            db.refresh(c)
            
        # Return newly generated AND existing pending candidates for this request
        all_pending = db.query(LearningCandidate).filter(LearningCandidate.status == CandidateStatus.PENDING).all()
        return all_pending
        
    def get_candidates(self, db: Session, status: Optional[CandidateStatus] = None) -> List[LearningCandidate]:
        query = db.query(LearningCandidate)
        if status:
            query = query.filter(LearningCandidate.status == status)
        return query.all()

    def get_candidate(self, db: Session, candidate_id: str) -> Optional[LearningCandidate]:
        return db.query(LearningCandidate).filter(LearningCandidate.id == candidate_id).first()

feedback_learning_service = FeedbackLearningService()
