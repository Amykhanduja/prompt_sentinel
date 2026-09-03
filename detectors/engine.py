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

from semantic.semantic_engine import detect_semantic

from taxonomy.techniques import get_technique

from fusion import fuse_detections

import logging, json
from datetime import datetime, UTC
logger = logging.getLogger("promptsentinel")

def enrich_detection(detection: dict):
    """
    Adds taxonomy metadata to a detection.
    """

    metadata = get_technique(
        detection["technique"]
    )

    detection.setdefault(
        "name",
        metadata["name"]
    )

    detection.setdefault(
        "severity",
        metadata["severity"]
    )

    detection.setdefault(
        "family",
        metadata["family"]
    )

    return detection


def get_effective_learning_config() -> dict:
    from database.connection import SessionLocal
    from services.learning_configuration_service import learning_configuration_service
    try:
        with SessionLocal() as db:
            return learning_configuration_service.get_active_learning_config(db)
    except Exception as e:
        logger.error(f"Failed to fetch learning configuration: {e}")
        return {}

def run_detectors(
    prompt: str,
    source: str = "user",
    judge_info: dict = None
):
    active_config = get_effective_learning_config()

    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "detection_started"
    }))

    regex_detections = []

    regex_detectors = [

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

    # ------------------------------------------
    # Regex Detection
    # ------------------------------------------

    for detector in regex_detectors:

        result = detector(
            prompt,
            source
        )

        if not result:
            continue

        regex_detections.append(
            enrich_detection(result)
        )

    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "regex_completed",
        "regex_detections_count": len(regex_detections)
    }))

    # ------------------------------------------
    # Semantic Detection
    # ------------------------------------------

    semantic_detections = detect_semantic(
        prompt,
        source,
        active_config=active_config
    )

    for detection in semantic_detections:

        enrich_detection(
            detection
        )

    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "semantic_completed",
        "semantic_detections_count": len(semantic_detections)
    }))

    # ------------------------------------------
    # Fusion
    # ------------------------------------------

    detections = fuse_detections(
        regex_detections,
        semantic_detections
    )

    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "fusion_completed",
        "total_detections": len(detections)
    }))

    # ------------------------------------------
    # LLM Judge (Phase 17.3)
    # ------------------------------------------
    
    from llm.judge import evaluate_with_judge
    detections = evaluate_with_judge(prompt, detections, judge_info)

    return detections
