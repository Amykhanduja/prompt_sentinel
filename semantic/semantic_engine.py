from semantic.embeddings import (
    get_embedding,
    get_embeddings,
)

from semantic.similarity import (
    best_match,
)

from semantic.knowledge_base import (
    get_knowledge_base,get_positive_examples,
    get_negative_examples
)

from config import (
    DEFAULT_SIMILARITY_THRESHOLD,
)


class SemanticEngine:
    """
    Semantic detector based on embedding similarity.
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
                 "negative_embeddings": negative_embeddings
                 "threshold": entry.get("threshold",DEFAULT_SIMILARITY_THRESHOLD)
             }

    def detect(
        self,
        prompt: str,
        source: str = "input",
        top_k: int = 3
    ) -> list:

        if not prompt.strip():
            return []

        prompt_embedding = get_embedding(
            prompt
        )

        detections = []

        for technique, data in self.semantic_index.items():

            # ---------------------------------
            # Positive similarity
            # ---------------------------------

            rankings = rank_matches(
                prompt_embedding,
                data["embeddings"]
            )

            rankings = rankings[:top_k]

            if not rankings:
                continue

             best_index, best_similarity = rankings[0]

        # ---------------------------------
        # Technique threshold
        # ---------------------------------

            threshold = data.get(
                "threshold",
                DEFAULT_SIMILARITY_THRESHOLD
            )

            if best_similarity < threshold:
                continue

        # ---------------------------------
        # Negative similarity
        # ---------------------------------

            negative_similarity = 0.0

            negative_embeddings = data.get(
                "negative_embeddings"
            )

            if (
                negative_embeddings is not None
                and len(negative_embeddings) > 0
            ):

                _, negative_similarity = best_match(
                    prompt_embedding,
                    negative_embeddings
                )

                if negative_similarity >= best_similarity:
                    continue

        # ---------------------------------
        # Confidence score
        # ---------------------------------

            confidence = (
                best_similarity - threshold
            ) / (
                1.0 - threshold
            )

            confidence = max(
                0.0,
                min(
                    confidence,
                    1.0
                )
            )

        # ---------------------------------
        # Detection
        # ---------------------------------

            detections.append(
                {
                    "technique": technique,

                    "confidence": round(
                        confidence,
                        3
                    ),

                    "similarity": round(
                        best_similarity,
                        3
                    ),

                    "matched_example":
                        data["examples"][best_index],

                    "top_matches": [

                        {
                            "example":
                                data["examples"][index],

                            "similarity":
                                round(score, 3)
                        }

                        for index, score in rankings

                    ],

                    "match_explanation": {

                        "matched_example":
                             data["examples"][best_index],

                        "similarity":
                            round(best_similarity, 3),

                        "negative_similarity":
                            round(negative_similarity, 3),

                        "threshold":
                            threshold

                    },

                    "source": source,

                    "detector": "semantic"

                 }
            )

        detections.sort(
            key=lambda detection:
            detection["similarity"],
            reverse=True
        )

        return detections

def detect_semantic(
    prompt: str,
    source: str = "input"
):
    """
    Public API.
    """

    return _ENGINE.detect(
        prompt,
        source
    )
