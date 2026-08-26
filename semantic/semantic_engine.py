from semantic.embeddings import (
    get_embedding,
    get_embeddings,
)

from semantic.similarity import (
    best_match,
    rank_matches,
    cosine_similarity
)
from semantic.knowledge_base import (
    get_knowledge_base,get_positive_examples,
    get_negative_examples
)

from config import (
    DEFAULT_SIMILARITY_THRESHOLD,
    ENABLE_CROSS_ENCODER,
    SEMANTIC_MODE
)


class SemanticEngine:
    """
    Semantic detector based on embedding similarity or true classifier.
    """

    def __init__(self):
        self.knowledge_base = get_knowledge_base()
        self.semantic_index = {}
        self._build_index()

    def _build_index(self):
        """
        Generates embeddings for every semantic example.
        Executed only once during initialization.
        """
        for technique, entry in self.knowledge_base.items():
             examples = get_positive_examples(entry)
             embeddings = get_embeddings(examples)

             negative_examples = get_negative_examples(entry)
             negative_embeddings = get_embeddings(negative_examples)

             self.semantic_index[technique] = {
                 "examples": examples,
                 "embeddings": embeddings,
                 "negative_examples": get_negative_examples(entry),
                 "negative_embeddings": negative_embeddings,
                 "threshold": entry.get("threshold", DEFAULT_SIMILARITY_THRESHOLD)
             }
             
        # Always train classifier for the unified pipeline
        from semantic.classifier import train_classifier
        train_classifier(self.semantic_index)

    def retrieve_top_k(self, prompt: str, k: int = 20) -> list[dict]:
        """
        Phase 16 retrieval stage: Top-K cosine similarity candidates.
        """
        from semantic.embeddings import PROVIDER_VERSION
        from taxonomy.techniques import get_technique
        
        if not hasattr(self, "provider_version") or self.provider_version != PROVIDER_VERSION:
            self.semantic_index = {}
            self._build_index()
            self.provider_version = PROVIDER_VERSION

        if not prompt.strip():
            return []

        prompt_embedding = get_embedding(prompt)
        
        global_candidates = []
        for technique, data in self.semantic_index.items():
            if "embeddings" not in data or len(data["embeddings"]) == 0:
                continue
            rankings = rank_matches(prompt_embedding, data["embeddings"])
            for idx, orig_sim in rankings[:k]:
                global_candidates.append((technique, idx, orig_sim))
                
        global_candidates.sort(key=lambda x: x[2], reverse=True)
        global_candidates = global_candidates[:k]

        results = []
        for tech, idx, orig_sim in global_candidates:
            tech_meta = get_technique(tech)
            results.append({
                "technique_id": tech,
                "technique_name": tech_meta.get("name", tech),
                "example_text": self.semantic_index[tech]["examples"][idx],
                "embedding_similarity": float(orig_sim)
            })
            
        return results

    def rerank_candidates(self, prompt: str, candidates: list[dict], top_k: int = 3) -> list[dict]:
        """
        Phase 16 retrieval stage 2: Cross Encoder reranking.
        """
        if not candidates:
            return []
            
        from semantic.cross_encoder import predict_scores
        
        flat_candidates = [c["example_text"] for c in candidates]
        scores = predict_scores(prompt, flat_candidates)
        
        for candidate, score in zip(candidates, scores):
            candidate["cross_encoder_score"] = float(score)
            
        candidates.sort(key=lambda x: x.get("cross_encoder_score", 0.0), reverse=True)
        return candidates[:top_k]

    def detect(
        self,
        prompt: str,
        source: str = "input",
        top_k: int = 3,
        active_config: dict = None
    ) -> list:
        from semantic.embeddings import PROVIDER_VERSION
        
        if not hasattr(self, "provider_version") or self.provider_version != PROVIDER_VERSION:
            self.semantic_index = {}
            self._build_index()
            self.provider_version = PROVIDER_VERSION

        if not prompt.strip():
            return []

        prompt_embedding = get_embedding(prompt)
        
        # 1. Retrieve Top 20 candidates
        candidates = self.retrieve_top_k(prompt, k=20)
        
        # 2. Cross Encoder Reranking -> Top 3
        top_candidates = self.rerank_candidates(prompt, candidates, top_k=top_k)
        
        # 3. Restrict classifier allowed techniques
        allowed_techniques = list(set([c["technique_id"] for c in top_candidates]))
        
        # 4. Final detection with classifier
        return self._detect_unified(prompt_embedding, top_candidates, allowed_techniques, source, active_config)
        
    def _detect_unified(
        self,
        prompt_embedding,
        top_candidates,
        allowed_techniques,
        source: str,
        active_config: dict = None
    ) -> list:
        from semantic.classifier import predict
        from config import DEFAULT_SIMILARITY_THRESHOLD
        
        pred = predict(prompt_embedding, allowed_techniques)
        if not pred:
            return []
            
        predicted_pt = pred["predicted_pt"]
        if predicted_pt == "SAFE":
            return []
            
        detections = []
        for class_info in pred["top_3_classes"]:
            tech = class_info["technique"]
            if tech == "SAFE":
                continue
                
            prob = class_info["probability"]
            if prob < 0.16: # filter noise
                continue
                
            # Find the best candidate for this technique
            tech_candidates = [c for c in top_candidates if c["technique_id"] == tech]
            if not tech_candidates:
                continue
                
            best_candidate = tech_candidates[0]
                
            threshold = self.semantic_index[tech].get("threshold", DEFAULT_SIMILARITY_THRESHOLD)
            if active_config and "semantic" in active_config:
                threshold = active_config["semantic"]
                
            # Optionally check threshold against initial similarity
            if best_candidate["embedding_similarity"] < threshold:
                continue
                
            detection = {
                "technique": tech,
                "confidence": round(float(pred["confidence"]), 3),
                "similarity": round(float(best_candidate.get("cross_encoder_score", best_candidate["embedding_similarity"])), 3),
                "initial_similarity": round(float(best_candidate["embedding_similarity"]), 3),
                "reranked_score": round(float(best_candidate.get("cross_encoder_score", 0.0)), 3),
                "probability": round(float(prob), 3),
                "top_3_classes": pred["top_3_classes"],
                "source": source,
                "detector": "semantic_unified",
                "matched_example": best_candidate["example_text"],
                "top_matches": [
                    {
                        "example": c["example_text"],
                        "similarity": round(float(c.get("cross_encoder_score", c["embedding_similarity"])), 3),
                        "initial_similarity": round(float(c["embedding_similarity"]), 3)
                    }
                    for c in top_candidates if c["technique_id"] == tech
                ],
                "match_explanation": {
                    "predicted_class": predicted_pt,
                    "probability": round(float(prob), 3),
                    "confidence": round(float(pred["confidence"]), 3),
                    "cross_encoder_score": round(float(best_candidate.get("cross_encoder_score", 0.0)), 3),
                    "initial_similarity": round(float(best_candidate["embedding_similarity"]), 3)
                }
            }
            detections.append(detection)
            
        detections.sort(key=lambda x: x["probability"], reverse=True)
        return detections

_ENGINE = None

def detect_semantic(prompt: str, source: str = "input", active_config: dict = None):
    """
    Public API.
    """
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = SemanticEngine()
    return _ENGINE.detect(prompt, source, active_config=active_config)
