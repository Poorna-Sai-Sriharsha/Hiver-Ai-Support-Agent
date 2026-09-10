# Engineering Decision Log

This log documents the critical architectural and evaluation decisions made during the development of the Hiver AI Support Agent.

---

### Decision 01 — Brand Selection: AmazonHelp
**Context**: The project required a brand with sufficient data volume to support a RAG pipeline and diverse enough intents to test a classifier.
**Decision**: Selected **AmazonHelp**.
**Alternatives Considered**: AppleSupport, Delta.
**Why**: AmazonHelp provided the highest volume of usable (Customer $\rightarrow$ Brand) pairs (~155k) and a wide array of issues (from delivery to fraud), making it a robust testbed.
**Trade-off**: The high volume of "Delivery" queries creates a class imbalance that must be handled during evaluation.
**Status**: Implemented.

### Decision 02 — Conversation-Level Splitting
**Context**: Splitting data by individual tweets leads to leakage, where the model sees a question in Train and its answer in Test.
**Decision**: Split data by `conversation_id`.
**Alternatives Considered**: Random tweet-level split.
**Why**: This ensures that no part of a specific customer interaction is shared across splits, providing a honest measure of generalization.
**Trade-off**: Reduces the total number of available training pairs compared to tweet-level splitting.
**Status**: Implemented.

### Decision 03 — Intent Taxonomy (8 Categories)
**Context**: A generic "Support/Not Support" binary was insufficient for escalation logic.
**Decision**: Defined 8 specific intents based on TF-IDF clustering of AmazonHelp data.
**Alternatives Considered**: Using a generic dataset like Banking77.
**Why**: Amazon's support needs (e.g., "Kindle Activation") are fundamentally different from banking needs. Custom taxonomy ensures high relevance.
**Trade-off**: Higher annotation effort for the human golden set.
**Status**: Implemented.

### Decision 04 — Vector Store Fallback
**Context**: The system relies on `sentence-transformers`. If the environment lacks GPU or the library fails to load, the system would crash.
**Decision**: Implemented a stop-word filtered keyword-overlap fallback in `VectorStore`.
**Alternatives Considered**: No fallback (fail-fast).
**Why**: Ensures the system remains operational in resource-constrained environments.
**Trade-off**: Keyword search is significantly less accurate than semantic embeddings.
**Status**: Implemented.

### Decision 05 — Hybrid Escalation Policy
**Context**: LLMs are often over-confident and may "auto-handle" cases that are legally or security-sensitive.
**Decision**: Combined deterministic signals (low retrieval score, sensitive intent) with LLM reasoning.
**Alternatives Considered**: Pure LLM-based escalation.
**Why**: Deterministic signals provide a "safety floor" that cannot be bypassed by LLM hallucinations.
**Trade-off**: May increase the False-Escalation rate (lower auto-handle rate).
**Status**: Implemented.

### Decision 06 — Grounding via Claim-Support Verification
**Context**: Simple similarity scores do not guarantee that the generated response is factually supported by the evidence.
**Decision**: Implemented a pipeline that extracts claims from the reply and verifies them individually against evidence.
**Alternatives Considered**: Simple ROUGE/BLEU scores.
**Why**: Claim-level verification is the only way to detect specific hallucinations in a support context.
**Trade-off**: Significantly increases LLM API costs and latency per response.
**Status**: Implemented.

### Decision 07 — TF-IDF as Simple Baseline
**Context**: To prove the value of the AI Agent, a baseline was needed.
**Decision**: Used TF-IDF + Logistic Regression as the "Simple" baseline.
**Alternatives Considered**: Random guess or Majority class only.
**Why**: It represents a traditional "keyword-based" support bot, providing a clear benchmark for semantic improvement.
**Status**: Implemented.

### Decision 08 — Pydantic for Structured LLM Output
**Context**: LLM responses are occasionally malformed JSON, causing system crashes.
**Decision**: Used Pydantic models for all LLM-to-System interfaces.
**Alternatives Considered**: Manual regex parsing.
**Why**: Pydantic provides strict type validation and automatic error handling, ensuring system stability.
**Status**: Implemented.

### Decision 09 — Demo Mode (Sampled Reconstruction)
**Context**: Processing 3M+ rows of raw CSV data exceeds the memory limits of standard laptops.
**Decision**: Implemented a `--demo` flag that samples raw data *before* reconstruction.
**Alternatives Considered**: Forcing the use of high-memory cloud instances.
**Why**: Increases accessibility for reviewers and developers.
**Trade-off**: Demo mode results are an approximation and not suitable for final evaluation.
**Status**: Implemented.

### Decision 10 — LLM-as-a-Judge for Response Quality
**Context**: Manual scoring of 1000+ responses is infeasible.
**Decision**: Implemented an LLM judge based on a 7-dimension rubric.
**Alternatives Considered**: BERTScore or BLEU.
**Why**: Semantic quality in support (tone, helpfulness) cannot be captured by n-gram overlap metrics.
**Status**: Implemented.
