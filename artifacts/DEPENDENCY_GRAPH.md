# Dependency Graph

## High-Level Flow
`scripts/download_data.py` $\rightarrow$ `data/twcs.csv`
$\downarrow$
`scripts/profile_data.py` $\rightarrow$ `artifacts/data_profile.json`
$\downarrow$
`scripts/prepare_data.py` $\rightarrow$ `src/preprocessing/dataset_processor.py` $\rightarrow$ `data/processed/*.csv`
$\downarrow$
`src/retrieval/vector_store.py` $\leftarrow$ (Index build script missing: `scripts/build_index.py`)
$\downarrow$
`src/agent.py` (The Orchestrator)
  $\rightarrow$ `src/intent/ai_classifier.py` (Intent Classification)
  $\rightarrow$ `src/retrieval/vector_store.py` (Knowledge Retrieval)
  $\rightarrow$ `src/generation/ai_generator.py` (Response Generation)
  $\rightarrow$ `src/generation/safety_guard.py` (Safety Check)
  $\rightarrow$ `src/escalation/escalation_system.py` (Escalation Logic)
$\downarrow$
`src/evaluation/run.py` $\rightarrow$ `src/evaluation/evaluator.py` $\rightarrow$ `src/evaluation/llm_judge.py`
$\downarrow$
`app.py` (Streamlit Dashboard)

## Module Dependencies
- `src.agent` depends on: `llm_client`, `vector_store`, `ai_classifier`, `ai_generator`, `escalation_system`, `safety_guard`.
- `src.evaluation.run` depends on: `SupportAgent`, `TrivialIntentClassifier`, `SimpleIntentClassifier`, `VectorStore`, `LLMClient`.
- `src.retrieval.vector_store` depends on: `sentence_transformers`.
- `src.utils.llm_client` depends on: `anthropic`, `openai`.
