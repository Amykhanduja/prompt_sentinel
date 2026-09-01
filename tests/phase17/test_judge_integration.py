import pytest
from unittest.mock import patch, MagicMock
from detectors.engine import run_detectors
from llm.judge import merge_judge_decision

patch_semantic = patch("detectors.engine.detect_semantic", return_value=[])

@patch("llm.judge.LLM_JUDGE_ENABLED", False)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_disabled(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Medium"}]
        res = run_detectors("ambiguous prompt")
        mock_get_provider.assert_not_called()
        assert len(res) == 1
        assert res[0]["technique"] == "PT-009"

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_high_confidence(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "High"}]
        res = run_detectors("bad prompt")
        mock_get_provider.assert_not_called()
        assert len(res) == 1

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_medium_confidence(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Medium", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "MALICIOUS", "technique_id": "PT-009", "confidence": 0.8, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        res = run_detectors("ambiguous prompt")
        provider_mock.evaluate.assert_called_once()
        assert res[0]["judge_used"] is True

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_low_confidence(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Low", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "MALICIOUS", "technique_id": "PT-009", "confidence": 0.8, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        res = run_detectors("ambiguous prompt")
        provider_mock.evaluate.assert_called_once()
        assert res[0]["judge_used"] is True

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_malicious(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Low", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "MALICIOUS", "technique_id": "PT-009", "confidence": 0.95, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        res = run_detectors("ambiguous prompt")
        assert len(res) == 1
        assert res[0]["judge_decision"] == "MALICIOUS"
        assert "judge_confidence" in res[0]

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_judge_safe(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Low", "detectors": ["semantic"]}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "SAFE", "confidence": 0.9, "reason": "test"}
        mock_get_provider.return_value = provider_mock
        res = run_detectors("ambiguous prompt")
        assert len(res) == 0

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_provider_failure(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Low"}]
        provider_mock = MagicMock()
        provider_mock.evaluate.side_effect = Exception("API Timeout")
        mock_get_provider.return_value = provider_mock
        res = run_detectors("ambiguous prompt")
        assert len(res) == 1
        assert "judge_decision" not in res[0]

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_invalid_judge_result(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = [{"technique": "PT-009", "confidence_level": "Low"}]
        provider_mock = MagicMock()
        provider_mock.evaluate.return_value = {"decision": "INVALID", "confidence": 1.5}
        mock_get_provider.return_value = provider_mock
        res = run_detectors("ambiguous prompt")
        assert len(res) == 1
        assert "judge_decision" not in res[0]

def test_strong_regex_safe_judge():
    detections = [{"technique": "PT-009", "confidence_level": "Medium", "detectors": ["regex"]}]
    judge_result = {"decision": "SAFE", "confidence": 0.9, "reason": "test"}
    res = merge_judge_decision(detections, judge_result)
    assert len(res) == 1
    assert res[0]["judge_decision"] == "SAFE"

@patch("llm.judge.LLM_JUDGE_ENABLED", True)
@patch("llm.provider.get_llm_provider")
@patch("detectors.engine.fuse_detections")
def test_no_detections(mock_fuse, mock_get_provider):
    with patch_semantic:
        mock_fuse.return_value = []
        res = run_detectors("hello")
        mock_get_provider.assert_not_called()
        assert len(res) == 0
