from fastapi import FastAPI
from pydantic import BaseModel

from preprocessing.pipeline import preprocess_prompt
from detectors.engine import run_detectors
from scoring.risk_engine import calculate_risk
from policies.policy_engine import decide_action
from logs.alert_logger import log_alert

app = FastAPI(title="PromptSentinel")


class PromptRequest(BaseModel):
    prompt: str

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
        "original_prompt": prompt,
        "processed_prompt": processed_prompt,
        "detections": detections,
        "risk": risk,
        "action": action
    }

@app.get("/")
def health_check():
    return {
        "service": "PromptSentinel",
        "status": "running"
    }


@app.post("/scan")
def scan(request: PromptRequest):
    return scan_prompt(request.prompt)
if __name__ == "__main__":

    prompt = input("Prompt> ")

    result = scan_prompt(prompt)

    print("\n=== Scan Result ===")
    print(result)
