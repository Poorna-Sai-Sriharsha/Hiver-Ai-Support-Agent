# Engineering Decision Log

## 1. Brand Selection: AmazonHelp
**Decision**: Selected AmazonHelp as the target brand.
**Reason**: Highest volume of usable pairs (~155k) and extreme diversity of issues, providing a robust testbed for both RAG and classification.
**Alternative**: AppleSupport.
**Why Rejected**: Slightly lower volume of resolved pairs in the sampled set.

## 2. Conversation-Level Splitting
**Decision**: Split data by `conversation_id` rather than individual tweets.
**Reason**: Prevents data leakage where a customer's question is in Train and the brand's answer is in Test.
**Impact**: Guaranteed that the model is tested on entirely unseen customer interactions.

## 3. Intent Taxonomy (8 Categories)
**Decision**: Defined 8 specific intents (Delivery, Refund, Account, etc.) rather than a generic 3-class system.
**Reason**: Allows for more granular escalation rules (e.g., Account security always escalates).
**Alternative**: Use Banking77 taxonomy.
**Why Rejected**: Amazon's issues (like "Delivery") are fundamentally different from banking issues.

## 4. TF-IDF as Simple Baseline
**Decision**: Used TF-IDF + Logistic Regression as the non-LLM baseline.
**Reason**: Provides a transparent, fast, and honest benchmark of "what can be solved with keywords".
**Impact**: Highlighted the value of semantic embeddings over raw keyword matching.

## 5. Vector Store Fallback
**Decision**: Implemented a keyword-overlap fallback in `VectorStore`.
**Reason**: Ensures the system remains operational even if `sentence-transformers` or `torch` fails in the environment.

## 6. Hybrid Escalation Policy
**Decision**: Combined LLM reasoning with deterministic signals (e.g., retrieval score < 0.3).
**Reason**: LLMs can be over-confident; hard signals provide a safety floor.

## 7. Safety Guard implementation
**Decision**: Added a post-generation check for PII and hallucinated numbers.
**Reason**: Critical for customer support to avoid leaking order IDs or inventing delivery dates.

## 8. Demo Mode (Sampled Reconstruction)
**Decision**: Implemented a `--demo` flag that samples the raw dataset *before* reconstruction.
**Reason**: Reduces memory usage from 4GB+ to <500MB, making the project runnable on standard laptops.

## 9. Chronological Evaluation Preference
**Decision**: Organized the internal schema with timestamps.
**Reason**: Real-world support systems face temporal drift; evaluating on the latest data is more representative.

## 10. Pydantic for Structured LLM Output
**Decision**: Used Pydantic for intent and escalation outputs.
**Reason**: Prevents system crashes due to malformed JSON from the LLM.
