#!/bin/bash
set -e
export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel_test"

echo "=== MODEL A: BGE (Baseline) ==="
python3 scripts/run_benchmark.py --dataset datasets/benchmark/subset --embedding-model BAAI/bge-base-en-v1.5 --warmup 0

echo "=== MODEL C: Multilingual MiniLM ==="
python3 scripts/run_benchmark.py --dataset datasets/benchmark/subset --embedding-model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --warmup 0

echo "=== MODEL B: Multilingual e5-base ==="
python3 scripts/run_benchmark.py --dataset datasets/benchmark/subset --embedding-model intfloat/multilingual-e5-base --warmup 0

