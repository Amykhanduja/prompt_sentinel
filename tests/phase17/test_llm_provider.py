import pytest
from llm.judge import validate_provider_output, JudgeValidationException, evaluate_with_judge
from llm.mock_provider import MockLLMProvider
import config

def test_validate_successful_malicious():
    output = {
        "decision": "MALICIOUS",
        "technique_id": "PT-018",
        "confidence": 0.91,
        "reason": "Test"
    }
    validated = validate_provider_output(output)
    assert validated["decision"] == "MALICIOUS"
    assert validated["technique_id"] == "PT-018"
    assert validated["confidence"] == 0.91

def test_validate_successful_safe():
    output = {
        "decision": "SAFE",
        "confidence": 0.95
    }
    validated = validate_provider_output(output)
    assert validated["decision"] == "SAFE"

def test_validate_invalid_confidence():
    output = {
        "decision": "SAFE",
        "confidence": 1.4
    }
    with pytest.raises(JudgeValidationException):
        validate_provider_output(output)

def test_validate_missing_decision():
    output = {
        "confidence": 0.91
    }
    with pytest.raises(JudgeValidationException):
        validate_provider_output(output)

def test_validate_unknown_technique():
    output = {
        "decision": "MALICIOUS",
        "technique_id": "UNKNOWN-999",
        "confidence": 0.91
    }
    with pytest.raises(JudgeValidationException):
        validate_provider_output(output)

def test_provider_exception_fallback(monkeypatch):
    monkeypatch.setattr(config, "LLM_JUDGE_ENABLED", True)
    monkeypatch.setattr(config, "LLM_JUDGE_PROVIDER", "mock")
    
    import llm.provider
    
    def mock_get_provider():
        provider = MockLLMProvider()
        provider.next_exception = Exception("Network timeout")
        return provider
        
    monkeypatch.setattr(llm.provider, "get_llm_provider", mock_get_provider)
    
    original_detections = [{"technique": "PT-018", "confidence_level": "Medium"}]
    
    result = evaluate_with_judge("prompt", original_detections)
    assert result == original_detections

def test_disabled_judge(monkeypatch):
    monkeypatch.setattr(config, "LLM_JUDGE_ENABLED", False)
    original_detections = [{"technique": "PT-018", "confidence_level": "Medium"}]
    
    result = evaluate_with_judge("prompt", original_detections)
    assert result == original_detections

def test_malformed_json_fallback(monkeypatch):
    monkeypatch.setattr(config, "LLM_JUDGE_ENABLED", True)
    
    import llm.provider
    
    def mock_get_provider():
        provider = MockLLMProvider()
        provider.next_result = "This is a string, not a dictionary"
        return provider
        
    monkeypatch.setattr(llm.provider, "get_llm_provider", mock_get_provider)
    original_detections = [{"technique": "PT-018"}]
    
    result = evaluate_with_judge("prompt", original_detections)
    assert result == original_detections
