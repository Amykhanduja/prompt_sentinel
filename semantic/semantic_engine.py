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
             
        from config import SEMANTIC_MODE
        if SEMANTIC_MODE == "classifier":
            from semantic.classifier import train_classifier
            train_classifier(self.semantic_index)

    def detect(
        self,
        prompt: str,
        source: str = "input",
        top_k: int = 3
    ) -> list:

        from semantic.embeddings import PROVIDER_VERSION
        from config import SEMANTIC_MODE
        
        if not hasattr(self, "provider_version") or self.provider_version != PROVIDER_VERSION:
            self.semantic_index = {}
            self._build_index()
            self.provider_version = PROVIDER_VERSION

        if not prompt.strip():
            return []

        prompt_embedding = get_embedding(prompt)
        
        if SEMANTIC_MODE == "classifier":
            return self._detect_classifier(prompt, prompt_embedding, source)
        else:
            return self._detect_nearest_neighbor(prompt, prompt_embedding, source, top_k)
            
    def _detect_classifier(self, prompt: str, prompt_embedding, source: str) -> list:
        from semantic.classifier import predict
        
        pred = predict(prompt_embedding)
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
                
            detection = {
                "technique": tech,
                "confidence": round(pred["confidence"], 3),
                "probability": round(prob, 3),
                "top_3_classes": pred["top_3_classes"],
                "source": source,
                "detector": "semantic_classifier",
                "match_explanation": {
                    "predicted_class": predicted_pt,
                    "probability": round(prob, 3),
                    "confidence": round(pred["confidence"], 3)
                }
            }
            detections.append(detection)
        
        return detections

    def _detect_nearest_neighbor(
        self,
        prompt: str,
        prompt_embedding,
        source: str,
        top_k: int
    ) -> list:
        # 1. Retrieve Top-20 candidates GLOBALLY across all techniques
        retrieval_k = 20 if ENABLE_CROSS_ENCODER else top_k
        
        global_candidates = []
        for technique, data in self.semantic_index.items():
            rankings = rank_matches(prompt_embedding, data["embeddings"])
            for idx, orig_sim in rankings[:retrieval_k]:
                global_candidates.append((technique, idx, orig_sim))
                
        global_candidates.sort(key=lambda x: x[2], reverse=True)
        global_candidates = global_candidates[:retrieval_k]

        # 2. Cross Encoder Reranking
        if ENABLE_CROSS_ENCODER and global_candidates:
            from semantic.cross_encoder import predict_scores
            
            flat_candidates = [self.semantic_index[tech]["examples"][idx] for tech, idx, _ in global_candidates]
            
            scores = predict_scores(prompt, flat_candidates)
            
            reranked_global_candidates = []
            for (tech, idx, orig_sim), score in zip(global_candidates, scores):
                reranked_global_candidates.append((tech, idx, score, orig_sim))
                
            reranked_global_candidates.sort(key=lambda x: x[2], reverse=True)
            final_candidates = reranked_global_candidates[:top_k]
        else:
            final_candidates = [(tech, idx, sim, sim) for tech, idx, sim in global_candidates[:top_k]]

        # 3. Group by technique for Detection
        technique_groups = {}
        for tech, idx, score, orig_sim in final_candidates:
            if tech not in technique_groups:
                technique_groups[tech] = []
            technique_groups[tech].append((idx, score, orig_sim))

        detections = []

        # 4. Filtering and Negative Matching
        for technique, candidates in technique_groups.items():
            best_index, best_score, best_orig_sim = candidates[0]
            
            threshold = self.semantic_index[technique].get("threshold", DEFAULT_SIMILARITY_THRESHOLD)
            if best_orig_sim < threshold:
                continue
                
            neg_embs = self.semantic_index[technique].get("negative_embeddings")
            negative_similarity = 0.0
            
            if neg_embs is not None and len(neg_embs) > 0:
                _, negative_similarity = best_match(prompt_embedding, neg_embs)
                
            if negative_similarity >= best_orig_sim:
                continue
                
            confidence = best_orig_sim - negative_similarity

            MIN_CONFIDENCE = 0.20
            if confidence < MIN_CONFIDENCE:
                continue

            confidence = max(0.0, min(confidence, 1.0))

            detections.append({
                "technique": technique,
                "confidence": round(confidence, 3),
                "similarity": round(best_orig_sim, 3) if not ENABLE_CROSS_ENCODER else round(best_score, 3),
                "initial_similarity": round(best_orig_sim, 3),
                "reranked_score": round(best_score, 3) if ENABLE_CROSS_ENCODER else None,
                "matched_example": self.semantic_index[technique]["examples"][best_index],
                "top_matches": [
                    {
                        "example": self.semantic_index[technique]["examples"][idx],
                        "similarity": round(score, 3),
                        "initial_similarity": round(orig_sim, 3)
                    }
                    for idx, score, orig_sim in candidates
                ],
                "match_explanation": {
                    "matched_example": self.semantic_index[technique]["examples"][best_index],
                    "similarity": round(best_orig_sim, 3) if not ENABLE_CROSS_ENCODER else round(best_score, 3),
                    "negative_similarity": round(negative_similarity, 3),
                    "threshold": threshold
                },
                "source": source,
                "detector": "semantic"
            })

        detections.sort(
            key=lambda detection: detection["similarity"],
            reverse=True
        )

        return detections

_ENGINE = SemanticEngine()
def detect_semantic(prompt: str, source: str = "input"):
    """
    Public API.
    """
    return _ENGINE.detect(prompt, source)
