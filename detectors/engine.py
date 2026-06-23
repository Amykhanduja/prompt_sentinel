from detectors.override_detector import detect_override
from detectors.extraction_detector import detect_extraction
from detectors.dan_detector import detect_dan

def run_detectors(prompt: str):

    detections = []

    detectors = [
        detect_override,
        detect_extraction,
        detect_dan
    ]

    for detector in detectors:

        result = detector(prompt)

        if result:
            detections.append(result)

    return detections
