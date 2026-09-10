# Repository Inventory

| File | Type | Lines | Purpose | Dependencies | Dependents | Executed | Tested | README Ref |
|---|---|---|---|---|---|---|---|---|
| `app.py` | Python | 179 | Streamlit Dashboard | `src.agent`, `src.retrieval.vector_store` | - | Yes | No | Yes |
| `src/agent.py` | Python | 76 | Orchestrator for the support agent | `src.utils.llm_client`, `src.retrieval.vector_store`, `src.intent.ai_classifier`, `src.generation.ai_generator`, `src.escalation.escalation_system`, `src.generation.safety_guard` | `app.py`, `src.evaluation.evaluator`, `scripts.adversarial_tests` | Yes | Yes | - |
| `src/intent/ai_classifier.py` | Python | - | LLM-based intent classification | `pydantic` | `src.agent` | Yes | Yes | Yes |
| `src/intent/trivial_baseline.py` | Python | - | Majority baseline classifier | `pandas` | `src.evaluation.run` | Yes | No | Yes |
| `src/retrieval/vector_store.py` | Python | - | Vector-based document retrieval | `numpy`, `pandas`, `sklearn`, `sentence_transformers` | `src.agent`, `app.py`, `src.evaluation.run`, `scripts.adversarial_tests` | Yes | Yes | Yes |
| `src/retrieval/simple_baseline.py` | Python | - | TF-IDF baseline classifier | `pandas`, `numpy`, `sklearn` | `src.evaluation.run` | Yes | No | Yes |
| `src/generation/ai_generator.py` | Python | - | LLM-based response generation | `pydantic` | `src.agent` | Yes | Yes | Yes |
| `src/generation/safety_guard.py` | Python | - | Input/Output safety filtering | `re` | `src.agent` | Yes | Yes | - |
| `src/escalation/escalation_system.py` | Python | - | Escalation logic and policy | `json` | `src.agent` | Yes | Yes | Yes |
| `src/evaluation/evaluator.py` | Python | - | Core evaluation logic | `src.agent` | `src.evaluation.run` | Yes | No | - |
| `src/evaluation/llm_judge.py` | Python | - | LLM-as-judge implementation | `pydantic` | `src.evaluation.run` | Yes | No | Yes |
| `src/evaluation/run.py` | Python | - | Evaluation pipeline execution | `pandas`, `numpy`, `sklearn`, `src.agent`, `src.utils.llm_client`, `src.intent.trivial_baseline`, `src.retrieval.simple_baseline`, `src.retrieval.vector_store` | - | Yes | No | Yes |
| `src/preprocessing/dataset_processor.py` | Python | - | Data cleaning and splitting | `pandas`, `numpy`, `re` | `scripts.prepare_data` | Yes | Yes | - |
| `src/utils/llm_client.py` | Python | - | Abstracted LLM API client | `requests`, `anthropic`, `openai`, `dotenv` | `src.agent`, `src.evaluation.run` | Yes | Yes | - |
| `scripts/download_data.py` | Python | 33 | Downloads dataset from Kaggle | `os`, `subprocess` | - | Yes | No | Yes |
| `scripts/prepare_data.py` | Python | 101 | Prepares cleaned splits | `src.preprocessing.dataset_processor` | - | Yes | No | Yes |
| `scripts/profile_data.py` | Python | 103 | Generates data profile | `pandas` | - | Yes | No | Yes |
| `scripts/discover_intents.py` | Python | 69 | Clusters data to discover intents | `sklearn.cluster.KMeans` | - | Yes | No | - |
| `scripts/validate_judge.py` | Python | 56 | Human-Judge agreement validation | `sklearn.metrics.cohen_kappa_score` | - | Yes | No | - |
| `scripts/adversarial_tests.py` | Python | 59 | Runs adversarial test cases | `src.agent`, `src.retrieval.vector_store` | - | Yes | No | - |
| `tests/test_core.py` | Python | 43 | Pytest core logic tests | `src.agent` | - | Yes | Yes | - |
| `README.md` | Markdown | 65 | Project documentation | - | - | - | - | - |
| `REPORT.md` | Markdown | 49 | Final results report | - | - | - | - | - |
| `DECISION_LOG.md` | Markdown | 47 | Engineering decision log | - | - | - | - | - |
| `INTENTS.md` | Markdown | 58 | Intent taxonomy definition | - | - | - | - | - |
| `evaluation/golden_set.csv` | CSV | 201 | Human-validated labels | - | `src.evaluation.run` | Yes | - | Yes |
