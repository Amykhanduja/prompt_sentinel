from sqlalchemy.orm import Session
from sqlalchemy import func, case, desc, cast, Date
from datetime import datetime, UTC, timedelta

from database.models.feedback import Feedback, FeedbackLabel
from database.models.models import Detection

class FeedbackAnalyticsService:
    def _safe_rate(self, count: int, total: int) -> float:
        if total == 0:
            return 0.0
        return round((count / total) * 100, 2)

    def get_feedback_summary(self, db: Session) -> dict:
        result = db.query(
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.label == FeedbackLabel.CORRECT, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.label == FeedbackLabel.FALSE_POSITIVE, 1), else_=0)).label("false_positive")
        ).one()
        
        total = result.total or 0
        correct = result.correct or 0
        false_positive = result.false_positive or 0
        false_negative = 0 # Currently not collected in Phase 18.2 but specified in requirements

        return {
            "total_feedback": total,
            "correct": correct,
            "false_positive": false_positive,
            "false_negative": false_negative,
            "correct_rate": self._safe_rate(correct, total),
            "false_positive_rate": self._safe_rate(false_positive, total),
            "false_negative_rate": 0.0
        }

    def get_feedback_by_technique(self, db: Session) -> dict:
        results = db.query(
            Feedback.technique,
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.label == FeedbackLabel.CORRECT, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.label == FeedbackLabel.FALSE_POSITIVE, 1), else_=0)).label("false_positive")
        ).group_by(Feedback.technique).all()
        
        techniques = []
        for r in results:
            if not r.technique:
                continue
            t_total = r.total or 0
            t_correct = r.correct or 0
            t_fp = r.false_positive or 0
            
            techniques.append({
                "technique": r.technique,
                "total": t_total,
                "correct": t_correct,
                "false_positive": t_fp,
                "false_negative": 0,
                "false_positive_rate": self._safe_rate(t_fp, t_total),
                "false_negative_rate": 0.0
            })
            
        return {"techniques": techniques}

    def get_feedback_by_detector(self, db: Session) -> dict:
        results = db.query(
            Detection.detector,
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.label == FeedbackLabel.CORRECT, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.label == FeedbackLabel.FALSE_POSITIVE, 1), else_=0)).label("false_positive")
        ).join(Detection, Feedback.detection_id == Detection.id).group_by(Detection.detector).all()
        
        detectors = []
        for r in results:
            if not r.detector:
                continue
            t_total = r.total or 0
            t_correct = r.correct or 0
            t_fp = r.false_positive or 0
            
            detectors.append({
                "detector": r.detector,
                "total": t_total,
                "correct": t_correct,
                "false_positive": t_fp,
                "false_negative": 0,
                "false_positive_rate": self._safe_rate(t_fp, t_total)
            })
            
        return {"detectors": detectors}

    def get_feedback_by_severity(self, db: Session) -> dict:
        results = db.query(
            Feedback.severity,
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.label == FeedbackLabel.CORRECT, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.label == FeedbackLabel.FALSE_POSITIVE, 1), else_=0)).label("false_positive")
        ).group_by(Feedback.severity).all()
        
        severity_list = []
        for r in results:
            if not r.severity:
                continue
            severity_list.append({
                "severity": r.severity,
                "total": r.total or 0,
                "correct": r.correct or 0,
                "false_positive": r.false_positive or 0,
                "false_negative": 0
            })
            
        return {"severity": severity_list}

    def get_feedback_trends(self, db: Session, days: int = 30) -> dict:
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        
        results = db.query(
            cast(Feedback.created_at, Date).label("date"),
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.label == FeedbackLabel.CORRECT, 1), else_=0)).label("correct"),
            func.sum(case((Feedback.label == FeedbackLabel.FALSE_POSITIVE, 1), else_=0)).label("false_positive")
        ).filter(Feedback.created_at >= cutoff_date).group_by(cast(Feedback.created_at, Date)).order_by(cast(Feedback.created_at, Date)).all()
        
        data = []
        for r in results:
            data.append({
                "date": r.date.strftime("%Y-%m-%d") if r.date else "",
                "total": r.total or 0,
                "correct": r.correct or 0,
                "false_positive": r.false_positive or 0,
                "false_negative": 0
            })
            
        return {
            "period_days": days,
            "data": data
        }

    def get_feedback_hotspots(self, db: Session, min_sample_size: int = 5) -> dict:
        tech_data = self.get_feedback_by_technique(db)
        
        hotspots = []
        for t in tech_data["techniques"]:
            if t["total"] >= min_sample_size and t["false_positive_rate"] > 20.0:
                hotspots.append({
                    "technique": t["technique"],
                    "total": t["total"],
                    "false_positive": t["false_positive"],
                    "false_positive_rate": t["false_positive_rate"]
                })
        
        # Sort by highest FP rate
        hotspots.sort(key=lambda x: x["false_positive_rate"], reverse=True)
        return {"techniques": hotspots}

    def generate_feedback_insights(self, db: Session, min_sample_size: int = 5) -> dict:
        insights = []
        
        det_data = self.get_feedback_by_detector(db)
        for d in det_data["detectors"]:
            if d["total"] >= min_sample_size and d["false_positive_rate"] > 25.0:
                insights.append({
                    "type": "false_positive_hotspot",
                    "detector": d["detector"],
                    "technique": "multiple",
                    "false_positive_rate": d["false_positive_rate"],
                    "sample_size": d["total"],
                    "message": f"Detector '{d['detector']}' has a high false-positive rate ({d['false_positive_rate']}%) and is a candidate for investigation."
                })
                
        tech_data = self.get_feedback_hotspots(db, min_sample_size)
        for t in tech_data["techniques"]:
            insights.append({
                "type": "false_positive_hotspot",
                "detector": "multiple",
                "technique": t["technique"],
                "false_positive_rate": t["false_positive_rate"],
                "sample_size": t["total"],
                "message": f"Technique '{t['technique']}' requires review due to a high false-positive rate ({t['false_positive_rate']}%)."
            })
            
        if not insights:
            # Check if total samples are low
            summary = self.get_feedback_summary(db)
            if summary["total_feedback"] < min_sample_size:
                insights.append({
                    "confidence": "insufficient_sample",
                    "message": "Not enough feedback data to generate statistically significant insights."
                })
                
        return {"insights": insights}

feedback_analytics_service = FeedbackAnalyticsService()
