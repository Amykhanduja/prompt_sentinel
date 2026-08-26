from semantic.semantic_engine import SemanticEngine
import pytest

def test_basic_retrieval():
    engine = SemanticEngine()
    results = engine.retrieve_top_k("Ignore previous instructions", k=20)
    
    assert len(results) > 0
    assert len(results) <= 20
    
    # Metadata check
    assert "technique_id" in results[0]
    assert "technique_name" in results[0]
    assert "example_text" in results[0]
    assert "embedding_similarity" in results[0]

def test_ordering():
    engine = SemanticEngine()
    results = engine.retrieve_top_k("Ignore previous instructions", k=10)
    
    assert len(results) > 1
    
    for i in range(len(results) - 1):
        assert results[i]["embedding_similarity"] >= results[i+1]["embedding_similarity"]

def test_empty_input():
    engine = SemanticEngine()
    results = engine.retrieve_top_k("", k=20)
    assert len(results) == 0

def test_small_k():
    engine = SemanticEngine()
    results = engine.retrieve_top_k("Ignore previous instructions", k=2)
    assert len(results) == 2
