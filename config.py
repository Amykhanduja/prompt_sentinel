"""
Central configuration for PromptSentinel.
"""

# =============================================================================
# Semantic Detection
# =============================================================================

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# Maximum number of texts encoded together
EMBEDDING_BATCH_SIZE = 32

# =============================================================================
# Semantic Detector Mode
# =============================================================================

# Options: "nearest_neighbor", "classifier"
SEMANTIC_MODE = "classifier"

# If SEMANTIC_MODE is "classifier", specify the model type.
# Options: "logistic_regression", "linear_svm", "mlp"
CLASSIFIER_TYPE = "logistic_regression"

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

# =============================================================================
# LLM Judge Configuration
# =============================================================================
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env relative to this file to ensure consistency across contexts
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)

LLM_JUDGE_ENABLED = os.getenv("LLM_JUDGE_ENABLED", "false").lower() == "true"
LLM_JUDGE_PROVIDER = os.getenv("LLM_JUDGE_PROVIDER", "mock")
LLM_JUDGE_TIMEOUT = int(os.getenv("LLM_JUDGE_TIMEOUT", "10"))
LLM_JUDGE_API_KEY = os.getenv("LLM_JUDGE_API_KEY", "")
LLM_JUDGE_MODEL = os.getenv("LLM_JUDGE_MODEL", "gemini-3.6-flash")
