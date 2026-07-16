import re
from rapidfuzz import fuzz

def match_patterns(
    prompt: str,
    patterns: list,
    technique: str,
    source: str = "user"
):
    text = prompt.lower()
    spaceless_text = "".join(text.split())

    # 1. First pass: exact matches and regex
    for pattern in patterns:
        if isinstance(pattern, dict):
            value = pattern["value"]
            pattern_type = pattern.get("type", "contains")

            if pattern_type == "regex":
                if re.search(value, text):
                    return {
                        "technique": technique,
                        "confidence": 0.90,
                        "matched": True,
                        "pattern": value,
                        "source": source
                    }
            else:
                if value.lower() in text:
                    return {
                        "technique": technique,
                        "confidence": 0.80,
                        "matched": True,
                        "pattern": value,
                        "source": source
                    }
        else:
            if pattern.lower() in text:
                return {
                    "technique": technique,
                    "confidence": 0.80,
                    "matched": True,
                    "pattern": pattern,
                    "source": source
                }

    # 2. Second pass: fuzzy matching for non-regex patterns
    for pattern in patterns:
        value = None
        min_similarity = 85.0
        min_token_overlap = 85.0
        max_edit_distance = None  # Rapidfuzz ratios mostly replace this, but we can configure thresholds

        if isinstance(pattern, dict):
            if pattern.get("type", "contains") == "regex":
                continue
            value = pattern["value"].lower()
            min_similarity = pattern.get("min_similarity", min_similarity)
            min_token_overlap = pattern.get("min_token_overlap", min_token_overlap)
        else:
            value = pattern.lower()

        if not value:
            continue
            
        spaceless_value = "".join(value.split())

        # Check standard partial ratio (catches typos, transpositions, insertions/deletions)
        sim = fuzz.partial_ratio(value, text)
        
        # Check token sort ratio (good for out-of-order words)
        overlap = fuzz.partial_token_sort_ratio(value, text)
        
        # Check spaceless ratio (good for extreme spacing attacks like "i g n o r e")
        spaceless_sim = fuzz.partial_ratio(spaceless_value, spaceless_text)

        best_score = max(sim, overlap, spaceless_sim)

        if best_score >= min_similarity or best_score >= min_token_overlap:
            # Map fuzzy score [0, 100] to a confidence [0.60, 0.79]
            # so it's lower than exact match (0.80) but still valid
            fuzzy_confidence = round(0.60 + (best_score / 100.0) * 0.19, 3)
            return {
                "technique": technique,
                "confidence": fuzzy_confidence,
                "matched": True,
                "pattern": value,
                "source": source,
                "detector": "fuzzy"
            }

    return None
