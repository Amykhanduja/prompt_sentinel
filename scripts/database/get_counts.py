import sys
from database.connection import SessionLocal
from database.models.models import Scan, Detection, Alert, Statistics, User
from database.models.learning import LearningCandidate, LearningCandidateReview
from database.models.feedback import Feedback

db = SessionLocal()
try:
    print(f"Scans: {db.query(Scan).count()}")
    print(f"Detections: {db.query(Detection).count()}")
    print(f"Alerts: {db.query(Alert).count()}")
    print(f"Statistics: {db.query(Statistics).count()}")
    print(f"Users: {db.query(User).count()}")
    print(f"Feedback: {db.query(Feedback).count()}")
    print(f"LearningCandidates: {db.query(LearningCandidate).count()}")
    print(f"LearningCandidateReviews: {db.query(LearningCandidateReview).count()}")
except Exception as e:
    print(e)
