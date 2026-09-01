import logging
from config import LLM_JUDGE_ENABLED
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
    if not LLM_JUDGE_ENABLED:
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

def evaluate_with_judge(prompt: str, detections: list) -> list:
    if not should_invoke_llm_judge(detections):
        return detections

    from llm.provider import get_llm_provider
    try:
        provider = get_llm_provider()
    except Exception as e:
        logger.error(f"Failed to instantiate LLM Provider: {e}")
        return detections
        
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

    try:
        raw_output = provider.evaluate(prompt, context)
        validated_result = validate_provider_output(raw_output)
    except Exception as e:
        logger.warning(f"LLM Judge evaluation failed: {e}")
        return detections

    return merge_judge_decision(detections, validated_result)
