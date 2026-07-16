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
    ENABLE_CROSS_ENCODER
)


class SemanticEngine:
    """
    Semantic detector based on embedding similarity and optional cross encoder reranking.
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

    def detect(
        self,
        prompt: str,
        source: str = "input",
        top_k: int = 3
    ) -> list:

        from semantic.embeddings import PROVIDER_VERSION
        if not hasattr(self, "provider_version") or self.provider_version != PROVIDER_VERSION:
            self.semantic_index = {}
            self._build_index()
            self.provider_version = PROVIDER_VERSION

        if not prompt.strip():
            return []

        prompt_embedding = get_embedding(prompt)
        
        # 1. Retrieve Top-20 candidates GLOBALLY across all techniques
        retrieval_k = 20 if ENABLE_CROSS_ENCODER else top_k
        
        global_candidates = []
        for technique, data in self.semantic_index.items():
            rankings = rank_matches(prompt_embedding, data["embeddings"])
            # We take Top-20 per technique first to reduce sorting overhead
            for idx, orig_sim in rankings[:retrieval_k]:
                global_candidates.append((technique, idx, orig_sim))
                
        # Sort globally by embedding similarity and take Top-20 overall
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
            # Take Top-3 overall
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
            
            # Use original embedding similarity for threshold check to maintain backwards compatibility and threshold tuning
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
