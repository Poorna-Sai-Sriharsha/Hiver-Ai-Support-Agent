# System Architecture: Hiver AI Support Agent

This document provides a detailed technical specification of the Hiver AI Support Agent, an evaluated prototype for grounded response generation and escalation based on historical Twitter customer-support interactions.

## 1. High-Level Architecture

The system implements a Retrieval-Augmented Generation (RAG) pipeline with a strict escalation layer. The flow is as follows:
`User Query` $\rightarrow$ `Intent Classification` $\rightarrow$ `Vector Retrieval` $\rightarrow$ `Grounded Generation` $\rightarrow$ `Claim Verification` $\rightarrow$ `Escalation Decision` $\rightarrow$ `Final Response`.

## 2. Data Layer

### 2.1 Raw Dataset
The system uses the `thoughtvector/customer-support-on-twitter` dataset. The primary focus is on the **AmazonHelp** brand.

### 2.2 Conversation Reconstruction
Twitter data is a flat list of tweets. The `DatasetProcessor` reconstructs conversations by:
1.  **Root Identification**: Traversing `in_response_to_tweet_id` to find the origin of each thread.
2.  **Grouping**: Assigning a unique `conversation_id` to all tweets in the same thread.
3.  **Normalization**: Using `TextCleaner` to replace mentions with `[USER]` and URLs with `[URL]`.
4.  **Pair Extraction**: Creating interaction pairs consisting of a `CUSTOMER` message followed immediately by a `BRAND` response.

### 2.3 Data Split Strategy
To prevent data leakage, splitting is performed at the **conversation level**:
-   **Mechanism**: Unique `conversation_id`s are shuffled and split (80% Train, 10% Validation, 10% Test).
-   **Leakage Prevention**: If a conversation is assigned to the Test set, no tweets from that conversation appear in the Retrieval Corpus (Train set). This ensures the model cannot "remember" the specific resolution for a test query.
-   **Verification**: The `VectorStore.verify_no_leakage` method audits the index against forbidden IDs.

## 3. Intent Classification

### 3.1 Taxonomy
The taxonomy is centrally defined in `config/intents.yaml`. It consists of 8 categories:
-   Delivery & Shipping
-   Refunds & Returns
-   Account & Security
-   Order Status & Tracking
-   Payment & Billing
-   Product Quality & Warranty
-   Customer Service Access
-   Severe Complaint / Fraud

### 3.2 Classifier Architecture
The `AIIntentClassifier` implements a structured LLM-based approach:
-   **Inference**: The customer query and the taxonomy are passed to the LLM.
-   **Structured Output**: The system enforces a JSON schema (via Pydantic) containing `intent`, `confidence`, `reason`, and `alternative_intents`.
-   **Fallback**: If JSON parsing fails, the system defaults to "General Inquiry" with 0.0 confidence.

## 4. Retrieval Architecture

### 4.1 Corpus Construction
The retrieval corpus consists of the `customer_message` $\rightarrow$ `historical_brand_response` pairs from the training set.

### 4.2 RAG Pipeline
1.  **Embedding Model**: Uses `all-MiniLM-L6-v2` from the `sentence-transformers` library.
2.  **Vector Index**: Customer messages are embedded and stored in a NumPy array.
3.  **Similarity Search**: Performs cosine similarity between the query embedding and the index.
4.  **Top-K Selection**: The top 3 most similar historical resolutions are retrieved as evidence.
5.  **Fallback**: If the embedding model fails to load, the system falls back to a stop-word filtered keyword overlap search.

## 5. Generation Architecture

### 5.1 Response Generation
The `AIResponseGenerator` synthesizes a reply using:
-   The customer query.
-   The predicted intent.
-   The top-3 retrieved historical resolutions.

### 5.2 Grounding and Claim Verification
To prevent hallucination, the system implements a **Claim-Support Verification** pipeline:
1.  **Claim Extraction**: The LLM extracts all factual claims (policies, actions, dates) from the draft reply.
2.  **Evidence Check**: Each claim is verified individually against the retrieved evidence.
3.  **Status Assignment**: Claims are marked as `SUPPORTED`, `PARTIALLY_SUPPORTED`, `UNSUPPORTED`, or `CONTRADICTED`.
4.  **Grounding Score**: Calculated as $\frac{\text{Supported Claims}}{\text{Total Claims}}$.

## 6. Escalation Architecture

The `EscalationSystem` decides whether to `AUTO-HANDLE` or `ESCALATE` using a hybrid policy.

### 6.1 Deterministic Signals
The system triggers an immediate escalation if any of the following are detected:
-   **Low Confidence**: Retrieval similarity score $< 0.3$.
-   **Sensitive Intent**: Intent is "Severe Complaint / Fraud" or "Account & Security".
-   **Risk Keywords**: Presence of terms like "legal", "court", "sue", or "fraud".

### 6.2 LLM Reasoning
For cases not caught by hard signals, the LLM evaluates the query and the draft reply to determine if the case requires human nuance.

### 6.3 Decision Flow
`Signals` $\rightarrow$ `LLM Reasoning` $\rightarrow$ `Final Decision` $\rightarrow$ `Reasoning String`.

## 7. Evaluation Architecture

### 7.1 Golden Set
-   **Size**: 200 examples.
-   **Sampling**: Randomly sampled from the test set.
-   **Labeling**: Manually annotated for `gold_intent` and `should_escalate`.
-   **Storage**: Stored in `evaluation/annotation_queue.csv`.

### 7.2 Automated Metrics
The `EvaluationHarness` calculates:
-   **Intent Accuracy/Macro-F1**: Compared against Trivial and Simple baselines.
-   **Escalation Precision/Recall**: Focuses on the "False Auto-Handle Rate".
-   **Grounding Score**: Average supported claim rate across the test set.

### 7.3 LLM-as-a-Judge
An independent LLM evaluates responses using a 0-4 scale across 7 dimensions:
-   Relevance, Correctness, Groundedness, Helpfulness, Tone, Safety, Completeness.
-   **Rubric**: Defined in `src/evaluation/llm_judge.py`.

### 7.4 Human Agreement
A subset (40-60 samples) is scored by a human using the same rubric. The correlation between human and LLM scores is used to validate the judge's reliability.
