import sys
import os
import time
import statistics

# Add the project root to sys.path so we can import internal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic.embeddings import set_provider, load_provider
from semantic.similarity import best_match
from semantic.knowledge_base import get_knowledge_base, get_positive_examples


def run_benchmark():
    models = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "BAAI/bge-base-en-v1.5",
        "thenlper/gte-large"
    ]
    
    kb = get_knowledge_base()
    
    # We will test using the first 5 techniques to keep it fast
    techniques_to_test = list(kb.keys())[:5]
    
    # Prepare test data: for each technique, we will pick 1 target and test other examples against it
    test_cases = []
    for technique in techniques_to_test:
        examples = get_positive_examples(kb[technique])
        if len(examples) >= 2:
            target = examples[0]
            queries = examples[1:5]
            test_cases.append((target, queries))
            
    print(f"Running benchmarks for {len(models)} models on {len(test_cases)} techniques...")
    print("-" * 60)
            
    results = {}
    
    for model_name in models:
        print(f"Loading {model_name}...")
        
        # Load the model and force it to be initialized
        set_provider(model_name)
        provider = load_provider()
        
        # Warmup
        provider.get_embedding("warmup")
        
        start_time = time.time()
        
        similarities = []
        
        for target, queries in test_cases:
            # Embed the target (simulating indexing)
            target_emb = provider.get_embeddings([target])
            
            for query in queries:
                query_emb = provider.get_embedding(query)
                _, sim = best_match(query_emb, target_emb)
                similarities.append(sim)
                
        end_time = time.time()
        
        runtime = end_time - start_time
        avg_sim = statistics.mean(similarities) if similarities else 0.0
        
        print(f"[{model_name}]")
        print(f"  Average Similarity: {avg_sim:.4f}")
        print(f"  Total Runtime:      {runtime:.4f} seconds")
        print("-" * 60)
        
        # Clean up
        provider.unload()

if __name__ == "__main__":
    run_benchmark()
