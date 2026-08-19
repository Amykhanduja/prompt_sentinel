import uuid
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List

from database.models.learning import (
    LearningCandidate, CandidateStatus, CandidateType,
    LearningApplication, ApplicationStatus,
    LearningConfig, LearningRule
)
from database.models.models import User

class LearningApplicationService:
    
    def apply_candidate(self, db: Session, candidate_id: str, applied_by: uuid.UUID) -> LearningApplication:
        candidate = db.query(LearningCandidate).filter(LearningCandidate.id == candidate_id).first()
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
            
        if candidate.status == CandidateStatus.PENDING:
            raise ValueError("Cannot apply a PENDING candidate")
        if candidate.status == CandidateStatus.REJECTED:
            raise ValueError("Cannot apply a REJECTED candidate")
            
        existing_app = db.query(LearningApplication).filter(
            LearningApplication.candidate_id == candidate_id,
            LearningApplication.status == ApplicationStatus.APPLIED
        ).first()
        if existing_app:
            raise ValueError(f"Candidate {candidate_id} has already been applied")

        # Validate supported types
        if candidate.candidate_type != CandidateType.THRESHOLD_ADJUSTMENT:
            raise ValueError(f"Unsupported candidate type for application: {candidate.candidate_type}")

        # Validate threshold bounds based on target
        # For simplicity, ensure proposed value is reasonable (e.g. 0.1 to 1.0)
        proposed_value = candidate.proposed_value
        if proposed_value is None or not (0.0 < proposed_value <= 1.0):
            raise ValueError("Proposed value must be between 0.0 and 1.0 for THRESHOLD_ADJUSTMENT")
            
        try:
            # Atomic application
            # 1. Create a new LearningConfig version
            current_active_config = db.query(LearningConfig).filter(LearningConfig.active == True).first()
            if current_active_config:
                current_active_config.active = False
                new_version = current_active_config.version + 1
            else:
                new_version = 1
                
            new_config = LearningConfig(
                version=new_version,
                active=True,
                created_by=applied_by
            )
            db.add(new_config)
            db.flush()
            
            # 2. Copy existing active rules if any
            if current_active_config:
                existing_rules = db.query(LearningRule).filter(
                    LearningRule.config_id == current_active_config.id,
                    LearningRule.enabled == True
                ).all()
                for rule in existing_rules:
                    new_rule = LearningRule(
                        config_id=new_config.id,
                        candidate_id=rule.candidate_id,
                        rule_type=rule.rule_type,
                        target=rule.target,
                        value=rule.value,
                        enabled=True
                    )
                    db.add(new_rule)
            
            # 3. Add the new learning rule
            new_rule = LearningRule(
                config_id=new_config.id,
                candidate_id=candidate.id,
                rule_type=candidate.candidate_type,
                target=candidate.target,
                value=proposed_value,
                enabled=True
            )
            db.add(new_rule)
            
            # 4. Create LearningApplication
            application = LearningApplication(
                candidate_id=candidate.id,
                config_id=new_config.id,
                applied_by=applied_by,
                version=new_version,
                change_type=candidate.candidate_type,
                target=candidate.target,
                previous_value=candidate.current_value,
                new_value=proposed_value,
                status=ApplicationStatus.APPLIED
            )
            db.add(application)
            
            # NOTE: Candidate remains APPROVED
            
            db.commit()
            db.refresh(application)
            return application
            
        except IntegrityError:
            db.rollback()
            raise ValueError("Duplicate application or concurrency conflict")
        except Exception as e:
            db.rollback()
            raise

    def rollback_application(self, db: Session, application_id: str, reason: str) -> LearningApplication:
        application = db.query(LearningApplication).filter(LearningApplication.id == application_id).first()
        if not application:
            raise ValueError(f"Application {application_id} not found")
            
        if application.status == ApplicationStatus.ROLLED_BACK:
            raise ValueError(f"Application {application_id} is already rolled back")
            
        try:
            application.status = ApplicationStatus.ROLLED_BACK
            application.rolled_back_at = datetime.now(UTC)
            application.rollback_reason = reason
            
            current_active_config = db.query(LearningConfig).filter(LearningConfig.active == True).first()
            if current_active_config:
                current_active_config.active = False
                
            # Create a new version config without this rule
            new_version = current_active_config.version + 1 if current_active_config else 1
            new_config = LearningConfig(
                version=new_version,
                active=True
            )
            db.add(new_config)
            db.flush()
            
            # Copy rules from current active config, excluding the one associated with this application's candidate
            if current_active_config:
                existing_rules = db.query(LearningRule).filter(
                    LearningRule.config_id == current_active_config.id,
                    LearningRule.enabled == True,
                    LearningRule.candidate_id != application.candidate_id
                ).all()
                for rule in existing_rules:
                    new_rule = LearningRule(
                        config_id=new_config.id,
                        candidate_id=rule.candidate_id,
                        rule_type=rule.rule_type,
                        target=rule.target,
                        value=rule.value,
                        enabled=True
                    )
                    db.add(new_rule)
                    
            db.commit()
            db.refresh(application)
            return application
            
        except Exception as e:
            db.rollback()
            raise

    def get_applications(self, db: Session, status: Optional[ApplicationStatus] = None) -> List[LearningApplication]:
        query = db.query(LearningApplication)
        if status:
            query = query.filter(LearningApplication.status == status)
        return query.all()
        
    def get_application(self, db: Session, application_id: str) -> Optional[LearningApplication]:
        return db.query(LearningApplication).filter(LearningApplication.id == application_id).first()

learning_application_service = LearningApplicationService()
