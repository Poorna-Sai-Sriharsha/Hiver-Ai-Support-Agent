#!/bin/bash
export PYTHONPATH=.
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=qwen2.5:7b-instruct
export OLLAMA_URL=http://127.0.0.1:11434

for i in $(seq 20 5 180); do
  echo "Processing small batch $i to $((i+5))..."
  python src/evaluation/run.py $i $((i+5))
  if [ $? -ne 0 ]; then
    echo "Batch $i failed. Stopping to prevent OOM loop."
    exit 1
  fi
  echo "Batch $i completed. Sleeping for 5s to clear memory..."
  sleep 5
done
echo "All small batches completed."
