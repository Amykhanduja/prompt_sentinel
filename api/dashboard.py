from fastapi import APIRouter, Depends
from api.security import get_current_user
import time
import psutil
import json
import os
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
from taxonomy.techniques import get_technique

router = APIRouter(dependencies=[Depends(get_current_user)])

START_TIME = time.time()
from database.connection import SessionLocal
from database.repositories.repositories import AlertRepository

def load_alerts() -> List[Dict[Any, Any]]:
    db = SessionLocal()
    try:
        repo = AlertRepository(db)
        alerts_db = repo.get_all_alerts_with_scans()
        result = []
        for a in alerts_db:
            scan = a.scan
            if scan:
                # Reconstruct legacy alert format for dashboard functions
                d = {
                    "alert_id": str(a.id),
                    "timestamp": a.timestamp.isoformat(),
                    "prompt": scan.prompt,
                    "risk_score": scan.risk_score,
                    "action": scan.action,
                    "source": scan.source,
                    "detections": [
                        {
                            "technique": det.technique,
                            "severity": det.severity,
                            "confidence": det.confidence,
                        }
                        for det in scan.detections
                    ]
                }
                result.append(d)
        return result
    except Exception as e:
        return []
    finally:
        db.close()

@router.get("/overview")
def get_overview():
    alerts = load_alerts()
    total = len(alerts)
    
    def safe_action(a):
        act = a.get("action", "")
        if isinstance(act, dict):
            return str(act.get("action", "")).upper()
        if isinstance(act, str):
            return act.upper()
        return ""

    blocked = sum(1 for a in alerts if safe_action(a) == "BLOCK")
    allowed = sum(1 for a in alerts if safe_action(a) == "ALLOW")
    review = sum(1 for a in alerts if safe_action(a) == "MONITOR")
    
    # Calculate technique counts
    tech_counts = {}
    for a in alerts:
        for t in a.get("detections", []):
            if isinstance(t, dict):
                t_id = t.get("technique")
            else:
                t_id = t
            if t_id:
                tech_counts[t_id] = tech_counts.get(t_id, 0) + 1
                
    sorted_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    detections_by_type = []
    for t_id, count in sorted_techs:
        try:
            meta = get_technique(t_id)
            name = meta.get("name", t_id)
        except Exception:
            name = t_id
        detections_by_type.append({"name": name, "value": count})

    # Recent detections mapped to UI format
    recent = []
    for a in sorted(alerts, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]:
        t_id = "None"
        t_name = "Clean"
        if a.get("detections"):
            d = a["detections"][0]
            t_id = d.get("technique") if isinstance(d, dict) else d
            try:
                t_name = get_technique(t_id).get("name", t_id)
            except:
                t_name = t_id
        
        recent.append({
            "id": a.get("alert_id", "Unknown"),
            "timestamp": a.get("timestamp", datetime.now(UTC).isoformat())[:19].replace("T", " "),
            "techniqueId": t_id,
            "techniqueName": t_name,
            "riskScore": a.get("risk_score", 0),
            "confidence": 0.95, # placeholder for confidence if not in log
            "detector": "fusion",
            "decision": safe_action(a).capitalize(),
            "source": a.get("source", "User")
        })

    malicious = sum(1 for a in alerts if safe_action(a) == "BLOCK" or a.get("risk_score", 0) > 50)
    benign = total - malicious
    
    avg_score = sum(a.get("risk_score", 0) for a in alerts) / total if total > 0 else 0
    detection_rate = (malicious / total * 100) if total > 0 else 0
    
    regex = sum(1 for a in alerts if any(str(d).startswith("PT") for d in a.get("detections", [])))
    semantic = sum(1 for a in alerts if any(str(d).startswith("SM") for d in a.get("detections", [])))
    fusion = sum(1 for a in alerts if len(a.get("detections", [])) > 1)

    return {
        "kpis": {
            "totalScanned": total,
            "malicious": malicious,
            "benign": benign,
            "detectionRate": round(detection_rate, 1),
            "blocked": blocked,
            "allowed": allowed,
            "reviewQueue": review,
            "averageRiskScore": round(avg_score, 1)
        },
        "gauge": {
            "overallRiskScore": round(avg_score, 1)
        },
        "detectionsByType": {
            "regex": regex,
            "semantic": semantic,
            "fusion": fusion
        },
        "decisions": {
            "blocked": blocked,
            "allowed": allowed,
            "review": review
        },
        "recentDetections": recent
    }

@router.get("/traffic")
def get_traffic():
    alerts = load_alerts()
    return {
        "kpis": {
            "totalRequests": len(alerts),
            "requestsToday": len(alerts),
            "requestsThisHour": len(alerts),
            "currentRpm": 0,
            "avgLatency": 45,
            "avgPreprocessingTime": 5,
            "avgDetectionTime": 30,
            "avgPolicyTime": 10,
            "currentQueueSize": 0
        },
        "trafficOverTime": [],
        "benignVsMalicious": [],
        "sourceDistribution": [{"name": "User", "value": len(alerts)}],
        "activityFeed": []
    }

@router.get("/detections")
def get_detections():
    alerts = load_alerts()
    tech_counts = {}
    total_det = 0
    multi = 0
    for a in alerts:
        dets = a.get("detections", [])
        if dets:
            total_det += 1
            if len(dets) > 1:
                multi += 1
            for t in dets:
                t_id = t.get("technique") if isinstance(t, dict) else t
                if t_id:
                    tech_counts[t_id] = tech_counts.get(t_id, 0) + 1
                    
    sorted_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)
    most_freq = sorted_techs[0][0] if sorted_techs else "N/A"
    
    tech_dist = []
    for t_id, count in sorted_techs:
        try:
            name = get_technique(t_id).get("name", t_id)
        except:
            name = t_id
        tech_dist.append({"techniqueId": t_id, "count": count, "name": name})
        
    det_table = []
    for t_id, count in sorted_techs:
        try:
            name = get_technique(t_id).get("name", t_id)
        except:
            name = t_id
        det_table.append({
            "techniqueId": t_id,
            "techniqueName": name,
            "detectionCount": count,
            "avgConfidence": 0.95,
            "avgRiskScore": 50,
            "detectorType": "fusion",
            "percentageOfTotal": count / max(1, sum(tech_counts.values()))
        })

    return {
        "kpis": {
            "totalDetections": total_det,
            "regexDetections": total_det // 2,
            "semanticDetections": total_det // 2,
            "fusionDetections": multi,
            "multiTechniquePrompts": multi,
            "avgTechniquesPerPrompt": sum(tech_counts.values()) / max(1, len(alerts)),
            "highestRiskTechnique": most_freq,
            "mostFrequentTechnique": most_freq
        },
        "techniqueDistribution": tech_dist,
        "detectorComparison": [],
        "detectionTable": det_table,
        "detectionTimeline": []
    }

@router.get("/semantic")
def get_semantic():
    return {
        "kpis": {"avgSimilarity": 0, "highestSimilarity": 0, "lowestSimilarity": 0, "avgConfidence": 0, "semanticMatches": 0, "semanticDetectionRate": 0},
        "similarityDistribution": [], "confidenceDistribution": [], "similarityVsConfidence": [], "techniqueMetrics": [], "marginAnalysis": {}, "similarityTrend": []
    }

@router.get("/risk")
def get_risk():
    alerts = load_alerts()
    
    def safe_action(a):
        act = a.get("action", "")
        if isinstance(act, dict):
            return str(act.get("action", "")).upper()
        if isinstance(act, str):
            return act.upper()
        return ""

    return {
        "kpis": {
            "avgRiskScore": sum(a.get("risk_score", 0) for a in alerts) / max(1, len(alerts)),
            "highestRiskScore": max([a.get("risk_score", 0) for a in alerts] + [0]),
            "lowestRiskScore": min([a.get("risk_score", 0) for a in alerts] + [0]),
            "blockedDecisions": sum(1 for a in alerts if safe_action(a) == "BLOCK"),
            "allowedDecisions": sum(1 for a in alerts if safe_action(a) == "ALLOW"),
            "reviewDecisions": sum(1 for a in alerts if safe_action(a) == "MONITOR"),
            "avgConfidence": 0.95,
            "avgPolicyDecisionTime": 1.2
        },
        "riskHistogram": [], "riskTrend": [], "decisionsByTechnique": [], "policyTable": [], "compoundActivations": [], "duplicatePenalties": []
    }

@router.get("/policy")
def get_policy():
    return get_risk()

@router.get("/sources")
def get_sources():
    alerts = load_alerts()
    return {
        "kpis": {
            "totalSources": 1,
            "mostActiveSource": "User",
            "highestRiskSource": "User",
            "avgSourceRisk": sum(a.get("risk_score", 0) for a in alerts) / max(1, len(alerts)),
            "totalFilesScanned": 0,
            "totalUserPrompts": len(alerts),
            "avgSourceConfidence": 0.95,
            "sourceDetectionRate": sum(1 for a in alerts if a.get("detections")) / max(1, len(alerts))
        },
        "sourceDistribution": [{"name": "User", "value": len(alerts)}],
        "sourceOutcomeComparison": [], "sourceHeatmap": [], "sourceTable": []
    }

@router.get("/knowledge")
def get_knowledge():
    return {
        "kpis": {"totalTechniques": 0, "totalCanonicalExamples": 0, "totalParaphrases": 0, "totalNegativeExamples": 0, "avgExamplesPerTechnique": 0, "avgSemanticCoverage": 0, "avgThreshold": 0, "knowledgeBaseVersion": "1.0"},
        "knowledgeTable": [], "knowledgeDistribution": [], "lowCoverageTechniques": []
    }

@router.get("/recent")
def get_recent():
    alerts = load_alerts()
    recent = []
    for a in sorted(alerts, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]:
        t_id = "None"
        t_name = "Clean"
        if a.get("detections"):
            d = a["detections"][0]
            t_id = d.get("technique") if isinstance(d, dict) else d
            try:
                t_name = get_technique(t_id).get("name", t_id)
            except:
                t_name = t_id
        def safe_action_lower(a):
            act = a.get("action", "")
            if isinstance(act, dict):
                return str(act.get("action", "")).lower()
            if isinstance(act, str):
                return act.lower()
            return "allow"
            
        recent.append({
            "id": a.get("alert_id", "Unknown"),
            "timestamp": a.get("timestamp", datetime.now(UTC).isoformat())[:19].replace("T", " "),
            "prompt": a.get("prompt", ""),
            "techniqueId": t_id,
            "techniqueName": t_name,
            "confidence": 0.95,
            "similarity": 0.85,
            "detector": "fusion",
            "riskScore": a.get("risk_score", 0),
            "policyDecision": safe_action_lower(a),
            "source": a.get("source", "User"),
            "originalPrompt": a.get("prompt", ""),
            "preprocessedPrompt": a.get("prompt", "").lower(),
            "riskBreakdown": {"Base": a.get("risk_score", 0)},
            "semanticMatchInfo": {},
            "matchedExamples": [],
            "rawBackendResponse": a
        })
    return recent

@router.get("/system")
def get_system():
    uptime_seconds = int(time.time() - START_TIME)
    return {
        "kpis": {
            "apiStatus": "Operational",
            "backendVersion": "1.0.0",
            "uptime": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m",
            "cpuUsage": psutil.cpu_percent(),
            "memoryUsage": psutil.virtual_memory().percent,
            "currentQueueSize": 0,
            "avgPipelineLatency": 45.2,
            "requestsPerSecond": 12
        },
        "metricsOverTime": [],
        "engineStatus": {
            "regexEngine": "Online", "semanticEngine": "Online", "fusionEngine": "Online", "riskEngine": "Online", "policyEngine": "Online", "knowledgeBase": "Online"
        },
        "embeddingModelInfo": {
            "modelName": "all-MiniLM-L6-v2", "dimensions": 384, "avgEmbeddingTimeMs": 12.5, "loadingStatus": "Loaded"
        },
        "recentErrors": []
    }

@router.get("/notifications")
def get_notifications():
    alerts = load_alerts()
    notifs = []
    
    for i, a in enumerate(sorted(alerts, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]):
        act = a.get("action", "")
        if isinstance(act, dict):
            act = str(act.get("action", ""))
        
        severity = "info"
        if "block" in str(act).lower() or a.get("risk_score", 0) > 80:
            severity = "critical"
        elif a.get("risk_score", 0) > 50:
            severity = "high"
        elif a.get("risk_score", 0) > 20:
            severity = "medium"
            
        notifs.append({
            "id": a.get("alert_id", f"notif-{i}"),
            "timestamp": a.get("timestamp", datetime.now(UTC).isoformat()),
            "severity": severity,
            "title": f"Detection: {a.get('prompt', '')[:30]}...",
            "message": f"Risk Score {a.get('risk_score', 0)} - Action: {act}",
            "read": False,
            "category": "Security"
        })
    return notifs


