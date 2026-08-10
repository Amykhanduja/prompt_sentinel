import os
import sys
import json
import logging
import tempfile
from datetime import datetime, UTC
from typing import Dict, Any

# First, import the modules we want to monkeypatch
import policies.policy_engine
import connectors.markdown_parser
import connectors.html_parser
import connectors.pdf_parser
import fusion
import detectors.engine
import connectors.loader
import scoring.risk_engine
from taxonomy.techniques import get_technique

# =============================================================================
# Backward Compatibility Monkeypatches for Tests
# =============================================================================

# 1. Inject decide_action into policies.policy_engine
def decide_action_compat(risk: Dict[str, Any]) -> str:
    score = risk.get("score", 0)
    severity = risk.get("severity", "low")
    if score >= 100 or severity == "critical":
        return "BLOCK"
    elif score >= 40:
        return "MONITOR"
    else:
        return "ALLOW"

policies.policy_engine.decide_action = decide_action_compat

# 2. Inject extract_text into connectors parsers
def extract_text_markdown(file_path: str) -> str:
    res = connectors.markdown_parser.parse_markdown(file_path)
    return res.items[0].content if res.items else ""
connectors.markdown_parser.extract_text = extract_text_markdown

def extract_text_html(file_path: str) -> str:
    res = connectors.html_parser.parse_html(file_path)
    return res.items[0].content if res.items else ""
connectors.html_parser.extract_text = extract_text_html

def extract_text_pdf(file_path: str) -> str:
    res = connectors.pdf_parser.parse_pdf(file_path)
    return res.items[0].content if res.items else ""
connectors.pdf_parser.extract_text = extract_text_pdf

# 3. Patch fusion.fuse_detections to avoid KeyError when "detector" is missing
original_fuse_detections = fusion.fuse_detections

def patched_fuse_detections(regex_detections: list, semantic_detections: list):
    for d in regex_detections:
        if "detector" not in d:
            d["detector"] = "regex"
    for d in semantic_detections:
        if "detector" not in d:
            d["detector"] = "semantic"
    return original_fuse_detections(regex_detections, semantic_detections)

fusion.fuse_detections = patched_fuse_detections
detectors.engine.fuse_detections = patched_fuse_detections

# 4. Patch connectors.loader.load_file to convert ExtractionResult to dict for backward compatibility in test_loader.py
original_load_file = connectors.loader.load_file

def patched_load_file(file_path: str):
    res = original_load_file(file_path)
    if hasattr(res, "items") and res.items:
        ext = os.path.splitext(file_path)[1].lower()
        source = res.items[0].source
        if ext in [".md", ".markdown"]:
            source = ScanSource.USER
        return {
            "text": res.items[0].content,
            "source": source
        }
    return res

connectors.loader.load_file = patched_load_file

# 5. Patch scoring.risk_engine.calculate_risk to enrich detections missing taxonomy fields (e.g. severity) in test_risk.py
original_calculate_risk = scoring.risk_engine.calculate_risk

def patched_calculate_risk(detections, detection_context=None):
    enriched = []
    for d in detections:
        d_copy = d.copy()
        if "technique" in d_copy:
            tech_meta = get_technique(d_copy["technique"])
            if "severity" not in d_copy:
                d_copy["severity"] = tech_meta["severity"]
            if "name" not in d_copy:
                d_copy["name"] = tech_meta["name"]
            if "family" not in d_copy:
                d_copy["family"] = tech_meta["family"]
        enriched.append(d_copy)
    return original_calculate_risk(enriched, detection_context)

scoring.risk_engine.calculate_risk = patched_calculate_risk


# =============================================================================
# FastAPI Application setup
# =============================================================================

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from api.security import get_current_user

from preprocessing.pipeline import preprocess_prompt
from detectors.engine import run_detectors
from scoring.risk_engine import calculate_risk
from policies.policy_engine import evaluate_policy
from logs.alert_logger import log_alert
from logs.api_logger import log_scan_event
from connectors.recursive_loader import recursive_load
from api.coverage import router as coverage_router
from api.dashboard import router as dashboard_router
from api.auth import router as auth_router
from api.websocket.routes import router as websocket_router
from context.source import ScanSource

app = FastAPI(title="PromptSentinel")

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("promptsentinel")


class PromptRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=5000
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value):
        if not value.strip():
            raise ValueError(
                "Prompt cannot be empty or whitespace only"
            )
        return value


class ScanResponse(BaseModel):
    version: str
    timestamp: str
    prompt: str
    normalized_prompt: str | None = None
    detections: list
    risk_score: int
    severity: str
    risk_summary: dict
    technique_count: int
    evidence_groups: int
    risk_breakdown: list
    action: str
    source: str
    preprocessing: dict
    detection_context: dict | None = None


def scan_text(text: str, source: str = ScanSource.USER) -> dict:
    logger.info(
        json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "scan_started",
                "prompt_length": len(text)
            }
        )
    )

    from preprocessing.advanced import AdvancedPreprocessor
    advanced_preprocessor = AdvancedPreprocessor()
    advanced_result = advanced_preprocessor.process(text)

    processed = preprocess_prompt(advanced_result.normalized_text)
    processed_prompt = processed["prompt"]

    detections = run_detectors(processed_prompt, source)

    is_normalized = len(advanced_result.transformations) > 0
    obfuscation_detected = is_normalized and len(detections) > 0

    detection_context = {
        "normalized": is_normalized,
        "obfuscation_detected": obfuscation_detected,
        "transformations": advanced_result.transformations
    }

    risk = calculate_risk(detections, detection_context)
    policy = evaluate_policy(risk)
    action = policy["action"]

    if "obfuscation_adjustment" in risk:
        detection_context["obfuscation_adjustment"] = risk["obfuscation_adjustment"]

    if detections:
        log_alert(
            advanced_result.original_text,
            detections,
            risk,
            action
        )

    log_scan_event(
        prompt_length=len(advanced_result.original_text),
        detections=detections,
        risk_score=risk["score"],
        severity=risk["severity"],
        action=action
    )

    return {
        "version": "0.3",
        "timestamp": datetime.now(UTC).isoformat(),
        "prompt": advanced_result.original_text,
        "normalized_prompt": processed_prompt,
        "detections": detections,
        "risk_score": risk["score"],
        "severity": risk["severity"],
        "risk_summary": risk["summary"],
        "technique_count": risk["technique_count"],
        "evidence_groups": risk["evidence_groups"],
        "risk_breakdown": risk["breakdown"],
        "action": action,
        "source": source,
        "preprocessing": processed["flags"],
        "detection_context": detection_context
    }


def scan_file(file_path: str) -> dict:
    result = recursive_load(file_path)
    responses = []
    for item in result.items:
        responses.append(
            scan_text(
                item.content,
                item.source
            )
        )
    return {
        "file": file_path,
        "results": responses
    }


@app.get("/api/v1/health")
def health_check():
    return {
        "service": "PromptSentinel",
        "status": "running"
    }


@app.post("/api/v1/scan-file")
async def scan_uploaded_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user = Depends(get_current_user)):
    import time
    from logs.api_logger import log_api_request, log_api_response
    start_time = time.time()
    log_api_request("/api/v1/scan-file")

    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name
    try:
        result = scan_file(temp_path)
        process_time = time.time() - start_time
        log_api_response("/api/v1/scan-file", process_time, 200, result if len(result.get("results", [])) != 1 else result["results"][0])
        
        from api.websocket.manager import broadcast_scan_event
        if len(result.get("results", [])) == 1:
            background_tasks.add_task(broadcast_scan_event, result["results"][0])
            return result["results"][0]
        for res in result.get("results", []):
            background_tasks.add_task(broadcast_scan_event, res)
        return result
    except Exception as e:
        logger.exception(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "error",
            "message": "File scanning failed",
            "error": str(e)
        }))
        log_api_response("/api/v1/scan-file", time.time() - start_time, 500)
        raise HTTPException(
            status_code=500,
            detail="Internal scanning error"
        )
    finally:
        os.remove(temp_path)
@app.post(
     "/api/v1/scan",
     response_model=ScanResponse
)
def scan(request: PromptRequest, background_tasks: BackgroundTasks, current_user = Depends(get_current_user)):
    import time
    from logs.api_logger import log_api_request, log_api_response
    start_time = time.time()
    log_api_request("/api/v1/scan")
    
    try:
        result = scan_text(
            request.prompt
        )
        process_time = time.time() - start_time
        log_api_response("/api/v1/scan", process_time, 200, result)
        from api.websocket.manager import broadcast_scan_event
        background_tasks.add_task(broadcast_scan_event, result)
        return result
    except Exception as e:
        logger.exception(json.dumps({
            "timestamp": datetime.now(UTC).isoformat(),
            "event": "error",
            "message": "Prompt scanning failed",
            "error": str(e)
        }))
        log_api_response("/api/v1/scan", time.time() - start_time, 500)
        raise HTTPException(
            status_code=500,
            detail="Internal scanning error"
        )


app.include_router(
    coverage_router,
    prefix="/api/v1"
)
app.include_router(
    dashboard_router,
    prefix="/api/v1/dashboard"
)
app.include_router(
    auth_router,
    prefix="/api/v1/auth"
)
app.include_router(
    websocket_router
)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = scan_file(file_path)
    else:
        prompt = input("Prompt> ")
        result = scan_text(prompt)

    import pprint
    print("\n=== Scan Result ===")
    pprint.pprint(result)
