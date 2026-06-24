from preprocessing.pipeline import preprocess_prompt
from detectors.engine import run_detectors
from scoring.risk_engine import calculate_risk
from policies.policy_engine import decide_action
from logs.alert_logger import log_alert


def scan_prompt(prompt: str):

    processed_prompt = preprocess_prompt(prompt)

    detections = run_detectors(processed_prompt)

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


if __name__ == "__main__":

    prompt = input("Prompt> ")

    result = scan_prompt(prompt)

    print("\n=== Scan Result ===")
    print(result)
