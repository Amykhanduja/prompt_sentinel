import pytest
from unittest.mock import patch, MagicMock
from detectors.engine import run_detectors

patch_semantic = patch("detectors.engine.detect_semantic", return_value=[])

@patch("config.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_observability_not_invoked(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "High"}]
        judge_info = {}
        res = run_detectors("bad prompt", judge_info=judge_info)
        assert judge_info["judge"]["outcome"] == "NOT_INVOKED"
        assert judge_info["judge"]["used"] is False

@patch("config.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_observability_confirmed(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Medium", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "MALICIOUS", "technique_id": "PT-009", "confidence": 0.5, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        judge_info = {}
        res = run_detectors("ambiguous prompt", judge_info=judge_info)
        
        assert judge_info["judge"]["outcome"] == "CONFIRMED"
        assert judge_info["judge"]["pre_judge_decision"] == "MALICIOUS"
        assert judge_info["judge"]["post_judge_decision"] == "MALICIOUS"
        assert judge_info["judge"]["used"] is True

@patch("config.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_observability_overridden(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Medium", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "SAFE", "confidence": 0.9, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        judge_info = {}
        res = run_detectors("ambiguous prompt", judge_info=judge_info)
        
        assert judge_info["judge"]["outcome"] == "OVERRIDDEN"
        assert judge_info["judge"]["pre_judge_decision"] == "MALICIOUS"
        assert judge_info["judge"]["post_judge_decision"] == "SAFE"

@patch("config.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_observability_escalated(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Medium", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "MALICIOUS", "technique_id": "PT-012", "confidence": 0.95, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        judge_info = {}
        res = run_detectors("ambiguous prompt", judge_info=judge_info)
        
        assert judge_info["judge"]["outcome"] == "ESCALATED"
        assert judge_info["judge"]["pre_judge_confidence"] == "Medium"
        assert judge_info["judge"]["post_judge_confidence"] == "Very High"

@patch("config.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_observability_fallback(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Medium", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.side_effect = Exception("API Timeout")
        mock_get_provider.return_value = provider_mock
        judge_info = {}
        res = run_detectors("ambiguous prompt", judge_info=judge_info)
        
        assert judge_info["judge"]["outcome"] == "FALLBACK"
        assert judge_info["judge"]["pre_judge_decision"] == "MALICIOUS"
        assert judge_info["judge"]["post_judge_decision"] == "MALICIOUS"

