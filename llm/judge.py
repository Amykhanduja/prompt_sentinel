import logging
import config
from taxonomy.techniques import get_technique

logger = logging.getLogger("promptsentinel")

class JudgeValidationException(Exception):
    pass

def validate_provider_output(output: dict) -> dict:
    if not isinstance(output, dict):
        raise JudgeValidationException("Provider output must be a JSON dictionary.")

    decision = output.get("decision")
    if decision not in ("SAFE", "MALICIOUS", "UNCERTAIN"):
        raise JudgeValidationException(f"Unknown decision: {decision}")

    confidence = output.get("confidence")
    if confidence is None or not isinstance(confidence, (int, float)):
        raise JudgeValidationException("Confidence must be a float.")
        
    if not (0.0 <= confidence <= 1.0):
        raise JudgeValidationException("Confidence must be between 0.0 and 1.0.")

    technique_id = output.get("technique_id")
    if decision == "MALICIOUS":
        if not technique_id:
            raise JudgeValidationException("MALICIOUS decision must include a technique_id.")
        
        tech_meta = get_technique(technique_id)
        if tech_meta.get("name") == "Unknown Technique":
            raise JudgeValidationException(f"Unknown technique_id: {technique_id}")

    return {
        "decision": decision,
        "technique_id": technique_id,
        "confidence": float(confidence),
        "reason": output.get("reason", "")
    }

def should_invoke_llm_judge(detections: list) -> bool:
    if not config.LLM_JUDGE_ENABLED:
        return False
    if not detections:
        return False
        
    highest_conf = detections[0].get("confidence_level")
    if highest_conf in ("Very High", "High"):
        return False
        
    return True

def merge_judge_decision(detections: list, judge_result: dict) -> list:
    decision = judge_result.get("decision", "UNCERTAIN")
    confidence = judge_result.get("confidence", 0.0)
    reason = judge_result.get("reason", "")
    technique_id = judge_result.get("technique_id")
    
    merged = []
    
    if decision == "SAFE":
        for d in detections:
            new_d = d.copy()
            new_d["judge_used"] = True
            new_d["judge_decision"] = decision
            new_d["judge_confidence"] = confidence
            new_d["judge_reason"] = reason
            
            is_regex = "regex" in new_d.get("detectors", [])
            is_high = new_d.get("confidence_level") in ("High", "Very High")
            
            if is_regex or is_high:
                merged.append(new_d)
        return merged
        
    elif decision == "MALICIOUS":
        for d in detections:
            new_d = d.copy()
            new_d["judge_used"] = True
            new_d["judge_decision"] = decision
            new_d["judge_confidence"] = confidence
            new_d["judge_reason"] = reason
            merged.append(new_d)
            
        existing_techs = [d.get("technique") for d in merged]
        if technique_id and technique_id not in existing_techs:
            tech_meta = get_technique(technique_id)
            confidence_pct = int(confidence * 100)
            if confidence_pct >= 90:
                level = "Very High"
            elif confidence_pct >= 75:
                level = "High"
            elif confidence_pct >= 50:
                level = "Medium"
            else:
                level = "Low"
                
            merged.append({
                "technique": technique_id,
                "name": tech_meta.get("name", "Unknown Technique"),
                "severity": tech_meta.get("severity", "LOW"),
                "family": tech_meta.get("family", "Unknown"),
                "detectors": ["llm_judge"],
                "sources": ["input"],
                "confidence": f"{confidence_pct}%",
                "confidence_level": level,
                "evidence": [f"LLM Judge reasoning: {reason}"],
                "judge_used": True,
                "judge_decision": decision,
                "judge_confidence": confidence,
                "judge_reason": reason
            })
        return merged
        
    else:
        for d in detections:
            new_d = d.copy()
            new_d["judge_used"] = True
            new_d["judge_decision"] = decision
            new_d["judge_confidence"] = confidence
            new_d["judge_reason"] = reason
            merged.append(new_d)
        return merged

def _get_highest_confidence(detections: list) -> str:
    if not detections:
        return "None"
    levels = {"Very High": 4, "High": 3, "Medium": 2, "Low": 1, "None": 0}
    highest = "None"
    for d in detections:
        conf = d.get("confidence_level", "None")
        if levels.get(conf, 0) > levels.get(highest, 0):
            highest = conf
    return highest

def evaluate_with_judge(prompt: str, detections: list, judge_info: dict = None) -> list:
    if judge_info is None:
        judge_info = {}
        
    pre_judge_decision = "MALICIOUS" if detections else "SAFE"
    pre_judge_confidence = _get_highest_confidence(detections)
    pre_judge_technique_id = detections[0].get("technique") if detections else None

    judge_data = {
        "used": False,
        "provider": None,
        "model": None,
        "decision": None,
        "confidence": None,
        "reason": None,
        "technique_id": None,
        "technique_name": None,
        "outcome": "NOT_INVOKED",
        "latency_ms": None,
        "pre_judge_decision": pre_judge_decision,
        "pre_judge_confidence": pre_judge_confidence,
        "pre_judge_technique_id": pre_judge_technique_id,
        "post_judge_decision": pre_judge_decision,
        "post_judge_confidence": pre_judge_confidence,
        "post_judge_technique_id": pre_judge_technique_id
    }
    judge_info["judge"] = judge_data

    if not should_invoke_llm_judge(detections):
        return detections

    from llm.provider import get_llm_provider
    try:
        provider = get_llm_provider()
    except Exception as e:
        logger.error(f"Failed to instantiate LLM Provider: {e}")
        judge_data["outcome"] = "FALLBACK"
        return detections
        
    judge_data["used"] = True
    judge_data["provider"] = provider.__class__.__name__
    judge_data["model"] = getattr(config, "LLM_JUDGE_MODEL", "Unknown")
        
    concise_detections = []
    for d in detections:
        concise_detections.append({
            "technique_id": d.get("technique"),
            "technique_name": d.get("name"),
            "confidence": d.get("confidence")
        })
        
    context = {
        "tentative_detections": concise_detections
    }

    import time
    start_time = time.monotonic()
    try:
        raw_output = provider.evaluate(prompt, context)
        validated_result = validate_provider_output(raw_output)
    except Exception as e:
        logger.warning(f"LLM Judge evaluation failed: {e}")
        judge_data["outcome"] = "FALLBACK"
        judge_data["latency_ms"] = int((time.monotonic() - start_time) * 1000)
        return detections
        
    latency_ms = int((time.monotonic() - start_time) * 1000)
    judge_data["latency_ms"] = latency_ms
    
    decision = validated_result.get("decision", "UNCERTAIN")
    confidence = validated_result.get("confidence", 0.0)
    reason = validated_result.get("reason", "")
    technique_id = validated_result.get("technique_id")
    
    judge_data["decision"] = decision
    judge_data["confidence"] = confidence
    judge_data["reason"] = reason
    judge_data["technique_id"] = technique_id
    if technique_id:
        tech_meta = get_technique(technique_id)
        judge_data["technique_name"] = tech_meta.get("name") if tech_meta else None

    merged = merge_judge_decision(detections, validated_result)
    
    post_judge_decision = "MALICIOUS" if merged else "SAFE"
    post_judge_confidence = _get_highest_confidence(merged)
    post_judge_technique_id = merged[0].get("technique") if merged else None
    
    levels = {"Very High": 4, "High": 3, "Medium": 2, "Low": 1, "None": 0}
    
    if pre_judge_decision == "MALICIOUS" and post_judge_decision == "SAFE":
        outcome = "OVERRIDDEN"
    elif pre_judge_decision == "SAFE" and post_judge_decision == "MALICIOUS":
        outcome = "ESCALATED"
    elif pre_judge_decision == "MALICIOUS" and post_judge_decision == "MALICIOUS":
        if levels.get(post_judge_confidence, 0) > levels.get(pre_judge_confidence, 0):
            outcome = "ESCALATED"
        else:
            outcome = "CONFIRMED"
    else:
        outcome = "CONFIRMED"
        
    judge_data["outcome"] = outcome
    judge_data["post_judge_decision"] = post_judge_decision
    judge_data["post_judge_confidence"] = post_judge_confidence
    judge_data["post_judge_technique_id"] = post_judge_technique_id

    return merged
