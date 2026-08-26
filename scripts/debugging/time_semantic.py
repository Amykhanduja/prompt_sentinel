import time
imports = [
    "semantic.embeddings",
    "semantic.similarity",
    "semantic.knowledge_base",
    "config"
]
for mod in imports:
    start = time.time()
    try:
        __import__(mod)
        end = time.time()
        print(f"{mod}: {end-start:.2f}s")
    except Exception as e:
        print(f"{mod}: Failed - {e}")
