from collections import defaultdict


def fuse_detections(
    regex_detections: list,
    semantic_detections: list
):
    """
    Merge detections from multiple detectors.
    """

    grouped = defaultdict(list)

    for detection in regex_detections:
        grouped[detection["technique"]].append(detection)

    for detection in semantic_detections:
        grouped[detection["technique"]].append(detection)

    fused = []

    for technique, detections in grouped.items():

        result = detections[0].copy()

        result["detectors"] = sorted(
            {
                d["detector"]
                for d in detections
            }
        )

        result["sources"] = sorted(
            {
                d["source"]
                for d in detections
            }
        )

        examples = []
        for d in detections:
            if "matched_example" in d:
                examples.append(d["matched_example"])
        result["matched_examples"] = list(dict.fromkeys(examples))

        # Calibrated Confidence
        has_regex = "regex" in result["detectors"]
        has_fuzzy = "fuzzy" in result["detectors"]
        
        semantic_dets = [d for d in detections if d["detector"] in ("semantic", "semantic_classifier")]
        
        evidence = []
        probability = None
        
        if not semantic_dets:
            if has_regex:
                score = 100
                evidence.append("Regex agreement")
            elif has_fuzzy:
                score = 85
                evidence.append("Fuzzy agreement")
            else:
                score = 50
        else:
            sem = semantic_dets[0]
            initial_sim = sem.get("initial_similarity", sem.get("similarity", 0.0))
            
            neg_sim = 0.0
            if "match_explanation" in sem and "negative_similarity" in sem["match_explanation"]:
                neg_sim = sem["match_explanation"]["negative_similarity"]
                
            reranked = sem.get("reranked_score")
            probability = sem.get("probability")
            
            # Base logic
            score = (initial_sim - neg_sim) * 100
            evidence.append(f"Embedding similarity: {initial_sim:.3f}")
            if neg_sim > 0:
                evidence.append(f"Negative similarity: {neg_sim:.3f}")
                
            if reranked is not None:
                score = (score + (reranked * 100)) / 2
                evidence.append(f"Cross encoder score: {reranked:.3f}")
                
            if probability is not None:
                score = (score + (probability * 100)) / 2
                evidence.append(f"Classifier probability: {probability:.3f}")
                
            if has_regex:
                score += 50
                evidence.append("Regex agreement")
            
            if has_fuzzy:
                score += 35
                evidence.append("Fuzzy agreement")
                
        score = max(0, min(100, score))
        
        if score >= 90:
            level = "Very High"
        elif score >= 75:
            level = "High"
        elif score >= 50:
            level = "Medium"
        else:
            level = "Low"
            
        result["confidence"] = f"{int(score)}%"
        result["probability"] = probability
        result["confidence_level"] = level
        result["evidence"] = evidence
        result["raw_confidence_score"] = score # for sorting

        fused.append(result)

    fused.sort(
        key=lambda x: x["raw_confidence_score"],
        reverse=True
    )
    
    for f in fused:
        f.pop("raw_confidence_score", None)

    return fused
