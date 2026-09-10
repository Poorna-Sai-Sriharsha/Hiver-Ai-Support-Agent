#!/bin/bash
export PYTHONPATH=.
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=qwen2.5:7b-instruct
export OLLAMA_URL=http://127.0.0.1:11434
for i in $(seq 0 20 180); do
  echo "Running batch $i to $((i+20))..."
  python src/evaluation/run.py $i $((i+20))
done
echo "All batches completed."
