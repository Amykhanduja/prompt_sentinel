import os
import json
import logging
import tempfile

from datetime import datetime
from typing import List

from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi import HTTPException
from pydantic import BaseModel , Field , field_validator

from preprocessing.pipeline import preprocess_prompt
from detectors.engine import run_detectors
from scoring.risk_engine import calculate_risk
from policies.policy_engine import decide_action
from logs.alert_logger import log_alert
from logs.api_logger import log_scan_event
from connectors.loader import load_file

app = FastAPI(title="PromptSentinel")

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

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
    detections: List[dict]
    risk_score: int
    severity: str
    action: str

class ErrorResponse(BaseModel):
    error: str

def scan_text(text):

    logger.info(
        json.dumps(
            {
                "event": "scan_started",
                "prompt_length": len(text)
            }
        )
    )

    processed = preprocess_prompt(text)

    processed_prompt = processed["prompt"]

    detections = run_detectors(processed_prompt)

    if processed["unicode_flag"]:
        detections.append({
            "technique": "PT-023",
            "description": "Unicode Obfuscation"
        })

    if processed["base64_flag"]:
        detections.append({
            "technique": "PT-024",
            "description": "Base64 Obfuscation"
        })

    risk = calculate_risk(detections)

    action = decide_action(risk)

    if detections:
        log_alert(
            text,
            detections,
            risk,
            action
        )

    return {
        "version": "0.3",
        "timestamp": datetime.utcnow().isoformat(),
        "detections": detections,
        "risk_score": risk["score"],
        "severity": risk["severity"],
        "action": action
    }

def scan_file(file_path: str):

    text = load_file(file_path)

    return scan_text(text)

@app.get("/api/v1/health")
def health_check():
    return {
        "service": "PromptSentinel",
        "status": "running"
    }


@app.post("/api/v1/scan-file")
async def scan_uploaded_file(file: UploadFile = File(...)):

    suffix = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:

        temp_file.write(await file.read())

        temp_path = temp_file.name

    try:

        result = scan_file(temp_path)

    finally:

        os.remove(temp_path)

    return result

@app.post(
     "/api/v1/scan",
     response_model=ScanResponse
)
def scan(request: PromptRequest):

    try:
        return scan_text(
            request.prompt
        )

    except Exception:

        logger.exception(
            "Prompt scanning failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Internal scanning error"
        )


if __name__ == "__main__":

    prompt = input("Prompt> ")

    result = scan_text(prompt)

    print("\n=== Scan Result ===")
    print(result)

