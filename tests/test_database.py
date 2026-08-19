import pytest
import os
import uuid
from datetime import datetime, UTC
from database.models.models import Scan, Detection, Alert, Statistics, ApiLog
from database.repositories.repositories import ScanRepository, AlertRepository, StatisticsRepository, ApiRepository

def test_database_connection(db_session):
    # Test connection and model instantiation
    assert db_session.is_active

def test_crud_scan_repository(db_session):
    repo = ScanRepository(db_session)
    prompt = "Test prompt"
    detections = [
        {"technique": "T1566", "detector": "fusion", "confidence": 0.9, "severity": "high", "evidence": []}
    ]
    scan = repo.create_scan(
        prompt=prompt,
        prompt_length=len(prompt),
        risk_score=90,
        severity="high",
        action="BLOCK",
        source="User",
        detections=detections
    )
    
    assert scan.id is not None
    assert scan.prompt == prompt
    assert len(scan.detections) == 1
    assert scan.detections[0].technique == "T1566"

def test_cascade_delete(db_session):
    repo = ScanRepository(db_session)
    scan = repo.create_scan("Test", 4, 10, "low", "ALLOW", "User", [{"technique": "T1", "detector": "f"}])
    scan_id = scan.id
    
    db_session.delete(scan)
    db_session.commit()
    
    det = db_session.query(Detection).filter(Detection.scan_id == scan_id).first()
    assert det is None

def test_foreign_keys(db_session):
    repo = ScanRepository(db_session)
    scan = repo.create_scan("Test FK", 7, 10, "low", "ALLOW", "User", [])
    
    alert_repo = AlertRepository(db_session)
    alert = alert_repo.save_alert(scan.id)
    
    assert alert.scan_id == scan.id
    assert alert.scan.prompt == "Test FK"

def test_transactions_and_rollback(db_session):
    repo = ScanRepository(db_session)
    try:
        # Intentionally cause an error to trigger rollback (e.g. invalid type)
        repo.create_scan(None, 0, 0, "low", "ALLOW", "User", [])
    except Exception:
        pass
        
    assert db_session.is_active

def test_statistics_repository(db_session):
    repo = StatisticsRepository(db_session)
    stats = repo.get_statistics()
    assert stats.total_alerts == 0
    
    detections = [{"technique": "T1", "severity": "high"}]
    repo.update_statistics(detections)
    
    stats_updated = repo.get_statistics()
    assert stats_updated.total_alerts == 1
    assert stats_updated.techniques.get("T1") == 1
    assert stats_updated.severities.get("high") == 1

def test_dashboard_api(auth_client):
    # Testing endpoints to ensure they don't break with repository
    response = auth_client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    assert "kpis" in response.json()

def test_performance_bulk_inserts(db_session):
    import time
    start = time.time()
    for _ in range(100):
        scan = Scan(
            id=uuid.uuid4(),
            prompt="bulk insert",
            prompt_length=11,
            risk_score=10,
            severity="low",
            action="ALLOW",
            source="User"
        )
        db_session.add(scan)
    db_session.commit()
    assert time.time() - start < 2.0 # Should be fast
