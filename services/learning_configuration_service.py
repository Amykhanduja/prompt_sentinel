from typing import Dict
from sqlalchemy.orm import Session
from database.models.learning import LearningConfig, LearningRule

class LearningConfigurationService:
    
    def get_active_learning_config(self, db: Session) -> Dict[str, float]:
        """
        Retrieves the active learning configuration.
        Returns a dictionary of {target: value}.
        This is a lightweight read-only method for the detection pipeline.
        """
        active_config = db.query(LearningConfig).filter(LearningConfig.active == True).first()
        if not active_config:
            return {}
            
        rules = db.query(LearningRule).filter(
            LearningRule.config_id == active_config.id,
            LearningRule.enabled == True
        ).all()
        
        # Currently only supports THRESHOLD_ADJUSTMENT where target is detector name and value is the threshold
        config_dict = {}
        for rule in rules:
            if rule.rule_type == "THRESHOLD_ADJUSTMENT":
                config_dict[rule.target] = rule.value
                
        return config_dict

learning_configuration_service = LearningConfigurationService()
