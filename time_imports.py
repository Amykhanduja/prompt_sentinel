import time
import sys

imports = [
    "preprocessing.pipeline",
    "detectors.engine",
    "scoring.risk_engine",
    "policies.policy_engine",
    "logs.alert_logger",
    "logs.api_logger",
    "connectors.recursive_loader",
    "context.source",
    "api.coverage",
    "api.dashboard",
    "api.auth",
    "api.feedback",
    "api.websocket.routes",
]

for mod in imports:
    start = time.time()
    try:
        __import__(mod)
        end = time.time()
        print(f"{mod}: {end-start:.2f}s")
    except Exception as e:
        print(f"{mod}: Failed - {e}")
