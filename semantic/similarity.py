import numpy as np


def cosine_similarity(vector1, vector2) -> float:
    """
    Computes cosine similarity between two embedding vectors.
    """

    if vector1 is None or vector2 is None:
        return 0.0

    denominator = (
        np.linalg.norm(vector1)
        * np.linalg.norm(vector2)
    )

    if denominator == 0:
        return 0.0

    similarity = np.dot(
        vector1,
        vector2
    ) / denominator

    return float(similarity)


def best_match(query_embedding, candidate_embeddings):
    """
    Returns:
        (best_index, similarity_score)
    """

    if candidate_embeddings is None or len(candidate_embeddings) == 0:
        return None, 0.0

    best_index = None
    best_score = -1.0

    for index, embedding in enumerate(candidate_embeddings):

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        if score > best_score:
            best_score = score
            best_index = index

    return best_index, float(best_score)


def rank_matches(query_embedding, candidate_embeddings):
    """
    Returns every example ranked by similarity.

    Returns:
        [
            (index, score),
            ...
        ]
    """

    if candidate_embeddings is None or len(candidate_embeddings) == 0:
        return []

    rankings = []

    for index, embedding in enumerate(candidate_embeddings):

        score = cosine_similarity(
            query_embedding,
            embedding
        )

        rankings.append(
            (
                index,
                float(score)
            )
        )

    rankings.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return rankings


def top_k_matches(
    query_embedding,
    candidate_embeddings,
    k=3
):
    """
    Returns the top-k most similar examples.

    Returns:
        [
            (index, score),
            ...
        ]
    """

    return rank_matches(
        query_embedding,
        candidate_embeddings
    )[:k]


def best_negative_match(
    query_embedding,
    negative_embeddings
):
    """
    Returns the strongest matching benign example.

    Returns:
        (index, similarity)
    """

    return best_match(
        query_embedding,
        negative_embeddings
    )


def confidence_score(
    positive_similarity,
    threshold
):
    """
    Converts similarity into a normalized confidence.

    Returns:
        float in [0,1]
    """

    if positive_similarity <= threshold:
        return 0.0

    confidence = (
        positive_similarity - threshold
    ) / (
        1.0 - threshold
    )

    return round(
        min(confidence, 1.0),
        3
    )


def passes_negative_filter(
    positive_similarity,
    negative_similarity,
    margin=0.05
):
    """
    Positive match must beat the best benign match.

    Example:

    malicious = 0.91
    benign    = 0.74

    -> True
    """

    return (
        positive_similarity >
        negative_similarity + margin
    )
}
