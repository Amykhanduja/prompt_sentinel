import logging

from datetime import datetime
from typing import List

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel , Field , field_validator

from preprocessing.pipeline import preprocess_prompt
from detectors.engine import run_detectors
from scoring.risk_engine import calculate_risk
from policies.policy_engine import decide_action
from logs.alert_logger import log_alert

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

def scan_prompt(prompt: str):

    processed = preprocess_prompt(prompt)

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
            prompt,
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


@app.get("/api/v1/health")
def health_check():
    return {
        "service": "PromptSentinel",
        "status": "running"
    }


@app.post(
     "/api/v1/scan",
     response_model=ScanResponse
)
def scan(request: PromptRequest):

    try:
        return scan_prompt(
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

    result = scan_prompt(prompt)

    print("\n=== Scan Result ===")
    print(result)
