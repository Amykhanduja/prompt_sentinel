from semantic.embeddings import (
    get_embedding,
    get_embeddings,
)

from semantic.similarity import (
    best_match,
)

from semantic.knowledge_base import (
    get_knowledge_base,
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

            examples = (
                entry["canonical_examples"] +
                entry["paraphrase_examples"]
            )

            embeddings = get_embeddings(
                examples
            )

            self.semantic_index[technique] = {
                "examples": examples,
                "embeddings": embeddings
            }

    def detect(
        self,
        prompt: str,
        source: str = "input"
    ) -> list:

        if not prompt.strip():
            return []

        prompt_embedding = get_embedding(
            prompt
        )

        detections = []

        for technique, data in self.semantic_index.items():

            index, similarity = best_match(
                prompt_embedding,
                data["embeddings"]
            )

            if similarity < DEFAULT_SIMILARITY_THRESHOLD:
                continue

            detections.append(
                {
                    "technique": technique,
                    "confidence": round(
                        similarity,
                        3
                    ),
                    "matched_example": data[
                        "examples"
                    ][index],
                    "source": source,
                    "detector": "semantic"
                }
            )

        detections.sort(
            key=lambda detection: detection[
                "confidence"
            ],
            reverse=True
        )

        return detections


_ENGINE = SemanticEngine()


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
