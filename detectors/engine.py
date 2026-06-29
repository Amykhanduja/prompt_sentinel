from detectors.override_detector import detect_override
from detectors.extraction_detector import detect_extraction
from detectors.dan_detector import detect_dan
from detectors.context_switch_detector import detect_context_switch
from detectors.delimiter_detector import detect_delimiter
from detectors.indirect_detector import detect_indirect
from detectors.tool_abuse_detector import detect_tool_abuse
from detectors.chained_detector import detect_chained
from detectors.template_detector import detect_template

def run_detectors(prompt: str):

    detections = []

    detectors = [
        detect_override,
        detect_extraction,
        detect_dan,
        detect_context_switch,
        detect_indirect,
        detect_delimiter,
        detect_tool_abuse,
        detect_chained,
        detect_template
    ]

    for detector in detectors:

        result = detector(prompt)

        if result:
            detections.append(result)

    return detections
