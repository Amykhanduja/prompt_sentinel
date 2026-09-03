import pytest
import json
import glob
import config
from semantic.knowledge_base import load_knowledge_base, get_knowledge_base

def test_taxonomy_loading():
    # Original taxonomy
    config.TAXONOMY_VERSION = "v1"
    kb_v1 = load_knowledge_base()
    
    # Expanded taxonomy
    config.TAXONOMY_VERSION = "v19_8"
    kb_v19_8 = load_knowledge_base()
    
    assert len(kb_v19_8) == len(kb_v1), "Number of techniques should be identical"
    
    # Check sizes
    pos1, pos2 = 0, 0
    neg1, neg2 = 0, 0
    
    for tech, entry in kb_v1.items():
        for k, v in entry.items():
            if k.endswith("_examples"):
                if k == "negative_examples": neg1 += len(v)
                else: pos1 += len(v)
                
    for tech, entry in kb_v19_8.items():
        for k, v in entry.items():
            if k.endswith("_examples"):
                if k == "negative_examples": neg2 += len(v)
                else: pos2 += len(v)
                
    assert pos2 > pos1, "Expanded taxonomy must have more positive examples"
    assert neg2 > neg1, "Expanded taxonomy must have more negative examples"

def test_benchmark_contamination():
    config.TAXONOMY_VERSION = "v19_8"
    kb = load_knowledge_base()
    
    samples = []
    with open("datasets/benchmark/v1/samples.jsonl") as f:
        for line in f:
            samples.append(json.loads(line)["prompt"].lower().strip())
            
    for tech, entry in kb.items():
        for k, v in entry.items():
            if k.endswith("_examples"):
                for ex in v:
                    ex_lower = ex.lower().strip()
                    assert ex_lower not in samples, f"Benchmark contamination detected: {ex}"

def test_db_isolation():
    from sqlalchemy import create_engine, text
    engine = create_engine("postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel_test")
    with engine.connect() as conn:
        feedback = conn.execute(text("SELECT COUNT(*) FROM feedback")).scalar()
        candidates = conn.execute(text("SELECT COUNT(*) FROM learning_candidates")).scalar()
        assert feedback == 0
        assert candidates == 0
