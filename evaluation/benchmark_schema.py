from typing import List, Optional, Union
from pydantic import BaseModel, Field
import enum

class BenchmarkLabel(str, enum.Enum):
    BENIGN = "benign"
    MALICIOUS = "malicious"

class BenchmarkDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class BenchmarkSample(BaseModel):
    id: str = Field(..., description="Stable unique identifier for the sample")
    prompt: str = Field(..., description="The prompt text to evaluate")
    label: BenchmarkLabel = Field(..., description="Ground truth deterministic label")
    attack_type: str = Field(..., description="High-level category (e.g. direct_adversarial, indirect_injection, benign)")
    subtype: Optional[str] = Field(None, description="Finer-grained classification")
    language: str = Field("en", description="Language characteristic (e.g., en, hi)")
    obfuscation: str = Field("none", description="Obfuscation method used, if any")
    difficulty: BenchmarkDifficulty = Field(..., description="Difficulty of detection")
    source: str = Field(..., description="How the sample was produced")
    expected_behavior: str = Field(..., description="What the detector should classify or do")

class BenchmarkDatasetVersion(BaseModel):
    dataset_name: str
    dataset_version: str
    description: Optional[str] = None
    samples: List[BenchmarkSample]
