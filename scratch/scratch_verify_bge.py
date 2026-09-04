import sys

def verify_bge():
    print("Checking if model is loaded before import...")
    import sys
    if "sentence_transformers" in sys.modules:
        print("FAIL: sentence_transformers loaded too early!")
        sys.exit(1)

    from semantic.embeddings import get_embedding, get_embeddings, model_name
    from semantic.providers import SentenceTransformerProvider

    print("Checking if model is loaded before usage...")
    if "sentence_transformers" in sys.modules:
        print("FAIL: sentence_transformers loaded during module import!")
        sys.exit(1)
        
    print("Model name from config:", model_name())
    if model_name() != "BAAI/bge-base-en-v1.5":
        print("FAIL: Incorrect model name!")
        sys.exit(1)

    print("Generating single embedding...")
    emb = get_embedding("Hello world")
    
    import numpy as np
    
    print("Single embedding type:", type(emb))
    print("Single embedding dtype:", emb.dtype)
    print("Single embedding shape:", emb.shape)
    
    if not isinstance(emb, np.ndarray):
        print("FAIL: Not a numpy array")
        sys.exit(1)
        
    if emb.shape != (768,):
        print("FAIL: Incorrect shape, expected (768,)")
        sys.exit(1)

    print("Generating batch embeddings...")
    embs = get_embeddings(["Hello", "World"])
    print("Batch embedding type:", type(embs))
    print("Batch embedding dtype:", embs.dtype)
    print("Batch embedding shape:", embs.shape)
    
    if embs.shape != (2, 768):
        print("FAIL: Incorrect batch shape, expected (2, 768)")
        sys.exit(1)
        
    norm = np.linalg.norm(emb)
    print("Norm:", norm)
    if not (0.99 < norm < 1.01):
        print("FAIL: Not normalized!")
        sys.exit(1)

    print("SUCCESS")

if __name__ == "__main__":
    verify_bge()
