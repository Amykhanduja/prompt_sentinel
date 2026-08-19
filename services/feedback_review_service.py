import uuid
from typing import List, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.models.learning import LearningCandidate, LearningCandidateReview, CandidateStatus

class FeedbackReviewService:
    def review_candidate(
        self,
        db: Session,
        candidate_id: str,
        reviewer_id: uuid.UUID,
        decision: CandidateStatus,
        comment: Optional[str]
    ) -> LearningCandidate:
        
        # Validations
        if decision not in [CandidateStatus.APPROVED, CandidateStatus.REJECTED]:
            raise ValueError(f"Invalid review decision: {decision}. Must be APPROVED or REJECTED.")
            
        if comment is not None:
            comment = comment.strip()
            if not comment:
                comment = None
            elif len(comment) > 1000:
                raise ValueError("Review comment exceeds maximum allowed length of 1000 characters.")

        # Load candidate
        candidate = db.query(LearningCandidate).filter(LearningCandidate.id == candidate_id).with_for_update().first()
        if not candidate:
            raise ValueError(f"Learning candidate '{candidate_id}' not found.")
            
        if candidate.status != CandidateStatus.PENDING:
            raise ValueError(f"Candidate is already {candidate.status.value}, cannot review.")

        # Create the review record
        review = LearningCandidateReview(
            candidate_id=candidate.id,
            reviewer_id=reviewer_id,
            decision=decision,
            comment=comment
        )
        
        db.add(review)
        
        # Update the candidate state
        candidate.status = decision
        candidate.reviewed_at = datetime.now(UTC)
        candidate.reviewed_by = reviewer_id
        
        try:
            db.commit()
            db.refresh(candidate)
            return candidate
        except IntegrityError:
            db.rollback()
            raise ValueError("A review already exists for this candidate.")
            
    def get_candidate_review(self, db: Session, candidate_id: str) -> Optional[LearningCandidateReview]:
        return db.query(LearningCandidateReview).filter(LearningCandidateReview.candidate_id == candidate_id).first()

feedback_review_service = FeedbackReviewService()
