"""
Central configuration for PromptSentinel.
"""

# =============================================================================
# Semantic Detection
# =============================================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Maximum number of texts encoded together
EMBEDDING_BATCH_SIZE = 32

# =============================================================================
# Cross Encoder Reranking
# =============================================================================

ENABLE_CROSS_ENCODER = True
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Force CPU even if CUDA is available
FORCE_CPU = False

# Normalize embeddings before similarity calculation
NORMALIZE_EMBEDDINGS = True

# =============================================================================
# Semantic Cache
# =============================================================================

ENABLE_EMBEDDING_CACHE = True

# =============================================================================
# Similarity Thresholds
# =============================================================================

DEFAULT_SIMILARITY_THRESHOLD = 0.75
