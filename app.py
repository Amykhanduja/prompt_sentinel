import os
import sys
import json
import logging
import tempfile
from datetime import datetime, UTC
from typing import Dict, Any

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
    judge: dict | None = None


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

    is_normalized = len(advanced_result.transformations) > 0
    
    # We pass a fresh dict to run_detectors to capture the judge metadata
    judge_info = {}
    detections = run_detectors(processed_prompt, source, judge_info=judge_info)

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

    judge_metadata = judge_info.get("judge") if judge_info else None

    if detections:
        log_alert(
            advanced_result.original_text,
            detections,
            risk,
            action,
            judge_metadata=judge_metadata
        )

    log_scan_event(
        prompt_length=len(advanced_result.original_text),
        detections=detections,
        risk_score=risk["score"],
        severity=risk["severity"],
        action=action,
        judge_metadata=judge_metadata
    )

    response = {
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
    if judge_metadata:
        response["judge"] = judge_metadata
        
    return response


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


from api.coverage import router as coverage_router
app.include_router(
    coverage_router,
    prefix="/api/v1"
)

from api.dashboard import router as dashboard_router
app.include_router(
    dashboard_router,
    prefix="/api/v1/dashboard"
)

from api.auth import router as auth_router
app.include_router(
    auth_router,
    prefix="/api/v1/auth"
)

from api.feedback import router as feedback_router
app.include_router(
    feedback_router,
    prefix="/api/v1/feedback"
)

from api.websocket.routes import router as websocket_router
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
