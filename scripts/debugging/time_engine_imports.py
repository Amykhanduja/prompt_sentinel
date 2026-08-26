import time

imports = [
    "detectors.override_detector",
    "detectors.extraction_detector",
    "detectors.dan_detector",
    "detectors.context_switch_detector",
    "detectors.delimiter_detector",
    "detectors.indirect_detector",
    "detectors.tool_abuse_detector",
    "detectors.chained_detector",
    "detectors.template_detector",
    "detectors.privileged_identity_detector",
    "detectors.output_leakage_detector",
    "detectors.api_wrapper_detector",
    "detectors.thought_simulation_detector",
    "detectors.format_token_detector",
    "detectors.stored_injection_detector",
    "detectors.metadata_detector",
    "detectors.api_response_detector",
    "semantic.semantic_engine",
    "taxonomy.techniques",
    "fusion"
]

for mod in imports:
    start = time.time()
    try:
        __import__(mod)
        end = time.time()
        print(f"{mod}: {end-start:.2f}s")
    except Exception as e:
        print(f"{mod}: Failed - {e}")
