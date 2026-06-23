from scoring.risk_engine import calculate_risk

detections = [
    {"technique": "PT-009"},
    {"technique": "PT-013"}
]

print(
    calculate_risk(detections)
)
