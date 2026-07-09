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
    Finds the most similar embedding from a list.

    Returns:
        (best_index, similarity_score)
    """

    if candidate_embeddings is None or len(candidate_embeddings) == 0 :
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

    return best_index, best_score


def rank_matches(query_embedding, candidate_embeddings):
    """
    Returns all candidates ranked by similarity.
    """

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
