from detectors.override_detector import detect_override
from detectors.extraction_detector import detect_extraction
from detectors.dan_detector import detect_dan
from detectors.context_switch_detector import detect_context_switch
from detectors.delimiter_detector import detect_delimiter
from detectors.indirect_detector import detect_indirect
from detectors.tool_abuse_detector import detect_tool_abuse
from detectors.chained_detector import detect_chained
from detectors.template_detector import detect_template
from detectors.privileged_identity_detector import detect_privileged_identity
from detectors.output_leakage_detector import detect_output_leakage
from detectors.api_wrapper_detector import detect_api_wrapper
from detectors.thought_simulation_detector import detect_thought_simulation
from detectors.format_token_detector import detect_format_token
from detectors.stored_injection_detector import detect_stored_injection
from detectors.metadata_detector import detect_metadata_injection
from detectors.api_response_detector import detect_api_response_injection

def run_detectors(prompt: str, source: str ="user"):

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
        detect_template,
        detect_privileged_identity,
        detect_api_wrapper,
        detect_output_leakage,
        detect_thought_simulation,
        detect_stored_injection,
        detect_format_token,
        detect_metadata_injection,
        detect_api_response_injection
    ]

    for detector in detectors:

        result = detector(prompt, source)

        if result:
            detections.append(result)

    return detections
