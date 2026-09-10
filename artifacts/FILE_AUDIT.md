# File Audit

| File | Purpose | Tested | Issues | Severity | Required Fix |
|---|---|---|---|---|---|
| `src/agent.py` | Orchestrates the full AI support pipeline. | Yes | None major. | INFO | - |
| `src/utils/llm_client.py` | Unified client for LLM providers. | Yes | `_call_anthropic` and `_call_openai` lack error handling (try-except); crashes on API error. | MEDIUM | Add robust try-except blocks for API calls. |
| `src/retrieval/vector_store.py` | Vector-based retrieval using SentenceTransformers. | Yes | Potential OOM on `model.encode` for large datasets. Hard-coded column name `historical_brand_response` may clash with dataset. | MEDIUM | Implement batch encoding for embeddings. Verify column names. |
| `src/intent/ai_classifier.py` | LLM-based intent classification with Pydantic validation. | Yes | Heuristic confidence mapping (e.g. "high" $\rightarrow$ 0.9). | LOW | Implement more robust confidence scoring if possible. |
| `src/generation/ai_generator.py` | Grounded response generation using RAG. | Yes | Grounding score is basic keyword overlap; likely inaccurate. | MEDIUM | Implement LLM-based grounding check or semantic overlap. |
| `src/escalation/escalation_system.py` | Hybrid escalation logic. | Yes | Misleading reason field: returns LLM reason even if signal triggered escalation. | MEDIUM | Fix reason logic to distinguish between signal and LLM triggers. |
| `src/generation/safety_guard.py` | PII and hallucination filtering. | Yes | Grounding check (number > 3 digits) is too crude; will cause false positives. | HIGH | Refine hallucination detection logic. |
| `src/evaluation/evaluator.py` | Evaluation harness. | No | `llm_judge_review` is completely mocked with a check for " la". | CRITICAL | Replace mock judge with real `LLMJudge` implementation. |
| `src/evaluation/llm_judge.py` | LLM-as-a-judge implementation. | No | Basic implementation, lacks consistency check. | LOW | Add repeated-run consistency testing. |
| `src/evaluation/run.py` | Full evaluation pipeline execution. | No | No error handling for missing artifact files. | LOW | Add file existence checks. |
| `src/preprocessing/dataset_processor.py` | Data cleaning and conversation reconstruction. | Yes | OOM risk in `_reconstruct` due to large `parent_map` dictionary for 3M rows. | HIGH | Use a more memory-efficient mapping or process in chunks. |
| `src/intent/trivial_baseline.py` | Majority class baseline. | No | None. | INFO | - |
| `src/retrieval/simple_baseline.py` | TF-IDF baseline. | No | Uses "simulated labels" (rules) to train ML model; not a true baseline. | MEDIUM | Use genuine labels or a pure rule-based system. |
| `scripts/build_index.py` | Index building script. | - | File is mentioned in README but missing from the repository. | CRITICAL | Create the missing `build_index.py` script. |
| `app.py` | Streamlit Dashboard. | No | Lacks error states for missing artifacts. | LOW | Add better error handling for missing JSON/CSV files. |
