import os
import pytest
import json
from config import LLM_JUDGE_API_KEY
from llm.provider import get_llm_provider

LIVE_TEST_ENABLED = os.environ.get("LLM_JUDGE_LIVE_TEST", "false").lower() == "true"
API_KEY_PROVIDED = bool(LLM_JUDGE_API_KEY)

if not (LIVE_TEST_ENABLED and API_KEY_PROVIDED):
    pytest.skip("Skipping live Gemini tests: LLM_JUDGE_LIVE_TEST=true and LLM_JUDGE_API_KEY must be set in the environment.", allow_module_level=True)

@pytest.mark.live
def test_gemini_provider_live():
    # We enforce provider is gemini and enabled for this test
    import config
    original_provider = config.LLM_JUDGE_PROVIDER
    original_enabled = config.LLM_JUDGE_ENABLED
    config.LLM_JUDGE_PROVIDER = "gemini"
    config.LLM_JUDGE_ENABLED = True
    
    try:
        # 1. Provider initializes successfully
        provider = get_llm_provider()
        assert provider.__class__.__name__ == "GeminiProvider"
        
        # 2, 3, 4, 7. Send request via end-to-end pipeline
        from detectors.engine import run_detectors
        
        # Safe controlled prompt that is ambiguous enough to trigger Judge
        # (Assuming it triggers a Medium/Low confidence semantic detection)
        prompt = "Explain how a SQL injection works theoretically."
        
        detections = run_detectors(prompt)
        
        # Since it's probabilistic, we just verify the pipeline didn't crash and the judge was either skipped or used safely
        assert isinstance(detections, list)
        
        # If judge was used, verify metadata
        for det in detections:
            if det.get("judge_used"):
                assert "judge_decision" in det
                assert det["judge_decision"] in ("MALICIOUS", "SAFE", "UNCERTAIN")
                assert "judge_confidence" in det
                assert isinstance(det["judge_confidence"], (int, float))
                assert 0.0 <= det["judge_confidence"] <= 1.0
                assert "judge_reason" in det
    finally:
        config.LLM_JUDGE_PROVIDER = original_provider
        config.LLM_JUDGE_ENABLED = original_enabled
