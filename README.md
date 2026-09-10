# Hiver AI Support Agent — Twitter Customer Support

This repository contains an evaluated support-agent prototype designed for grounded response generation and escalation on historical Twitter customer-support conversations. The system leverages a Retrieval-Augmented Generation (RAG) architecture to automate responses for **AmazonHelp** while maintaining strict safety guardrails to prevent hallucination and PII leakage.

## Problem Definition

The system is tasked with processing a customer-support message and executing the following pipeline:
1.  **Intent Identification**: Classifying the query into a specific support category (e.g., Delivery, Refund, Account Security).
2.  **Evidence Retrieval**: Fetching the most relevant historical "Query $\rightarrow$ Resolution" pairs from a curated corpus.
3.  **Grounded Generation**: Synthesizing a response based strictly on retrieved evidence.
4.  **Fact Verification**: Extracting factual claims from the generated response and verifying them against the retrieved evidence.
5.  **Escalation Decision**: Determining if the case can be automatically handled or requires human intervention based on risk signals.

### Engineering Challenges
-   **Ambiguity**: Twitter messages are often short, sarcastic, or missing critical context.
-   **Multi-intent Queries**: Users frequently ask multiple questions (e.g., "Where is my package AND I want a refund") in one message.
-   **Hallucination Risk**: LLMs may invent policies or dates if the retrieval evidence is insufficient.
-   **Safety Constraints**: High-risk categories (e.g., account security) must be escalated regardless of model confidence.

## System Architecture

### Data Pipeline
`Raw Kaggle Dataset` $\rightarrow$ `Conversation Reconstruction` $\rightarrow$ `Text Normalization` $\rightarrow$ `Leakage-Aware Splitting` $\rightarrow$ `Retrieval Corpus`.

### Inference Pipeline
`User Query` $\rightarrow$ `Intent Classifier` $\rightarrow$ `Vector Store (all-MiniLM-L6-v2)` $\rightarrow$ `Response Generator` $\rightarrow$ `Claim-Support Verifier` $\rightarrow$ `Escalation Engine` $\rightarrow$ `Final Response`.

### Evaluation Pipeline
`Golden Set (200 samples)` $\rightarrow$ `Automated Metrics` $\rightarrow$ `LLM-as-a-Judge` $\rightarrow$ `Human Judge Agreement` $\rightarrow$ `Metrics Artifacts`.

## Reproducibility

### 1. Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Dataset Acquisition
1. Place your `kaggle.json` in `~/.kaggle/` or `%USERPROFILE%\\.kaggle\\`.
2. Run the download script:
   ```bash
   python scripts/download_data.py
   ```

### 3. Execution Pipeline
Run the following commands in order to reproduce the system state and metrics:
```bash
# 1. Profile the raw data
python scripts/profile_data.py

# 2. Prepare cleaned data and splits (conversation-level)
python scripts/prepare_data.py

# 3. Build the retrieval index (SBERT embeddings)
python scripts/build_index.py

# 4. Run the full evaluation pipeline
python -m src.evaluation.run

# 5. Launch the internal operations dashboard
streamlit run app.py
```

**Demo Mode**: To run the pipeline on a sampled subset for faster verification, use:
`python scripts/prepare_data.py --demo`

## Configuration & Environment

The system requires the following environment variables:
- `ANTHROPIC_API_KEY`: Required for intent classification and response generation.
- `OPENAI_API_KEY`: (Optional) Alternative LLM provider.

Operational parameters, such as the intent taxonomy and brand selection, are managed in `config/config.yaml`.

## Evaluation Strategy

### Golden Set
The system is evaluated against a frozen "Golden Set" of 200 examples. This set is sampled from the test split and manually annotated for ground-truth intent and escalation status.

### Baselines
Performance is compared against two baselines:
-   **Trivial Baseline**: Predicts the most frequent intent (Majority Class).
-   **Simple Baseline**: TF-IDF based keyword classifier.

### LLM-as-a-Judge
Response quality is measured on a 0-4 scale across 7 dimensions: **Relevance, Correctness, Groundedness, Helpfulness, Tone, Safety, and Completeness**. The judge's reliability is validated by comparing its scores against human scores for a 60-sample subset.

## Evaluation Results

| Component | Metric | Result |
| :--- | :--- | :---: |
| Intent Classification | Macro F1 | Verified |
| Retrieval | Recall@3 | Verified |
| Grounding | Supported Claim Rate | Verified |
| Escalation | False Auto-Handle Rate | Verified |
| Response Quality | Human/LLM Judge Score | Pending |

## Detailed Documentation

For a deeper dive into the engineering decisions and system design, please refer to the following documents in the `docs/` directory:

### Technical Specifications
- [System Architecture](docs/ARCHITECTURE.md) — Detailed design of the RAG pipeline and components.
- [Intent Taxonomy](docs/INTENTS.md) — The single source of truth for support categories.
- [Security & Safety](docs/SECURITY.md) — PII handling and API resilience strategies.
- [Internal Operations Dashboard](docs/DASHBOARD.md) — Specification of the Streamlit internal tool.

### Evaluation & Analysis
- [Engineering Decision Log](docs/DECISION_LOG.md) — Records of critical trade-offs and alternatives.
- [Failure Analysis](docs/FAILURE_ANALYSIS.md) — Categorization of systematic model errors.
- [Headline Metric Analysis](docs/HEADLINE_NUMBER.md) — Intellectual honesty regarding performance results.
- [Final Documentation Audit](docs/FINAL_DOCUMENTATION_AUDIT.md) — Verification of repository readiness.

### Data & Reports
- [Executive Summary](docs/REPORT.md) — High-level project outcomes.
- [Brand Selection Report](docs/BRAND_SELECTION.md) — Justification for target brand choice.
- [Data Profiling](docs/DATA_PROFILE.md) — Analysis of the raw Twitter dataset.
- [Splitting Methodology](docs/DATA_SPLITTING_METHODOLOGY.md) — Technical approach to leakage prevention.
- [Final QA Report](docs/FINAL_QA_REPORT.md) — Results of the final verification pass.

## Repository Structure

```text
.
├── app.py                    # Streamlit Internal Ops Dashboard
├── README.md                 # Technical Documentation
├── requirements.txt          # Project Dependencies
├── config/                   # Taxonomy and Prompt Templates
│   └── config.yaml
├── src/                      # Core Logic
│   ├── preprocessing/         # Reconstruction and Cleaning
│   ├── intent/               # AI Classifier and Baselines
│   ├── retrieval/            # Vector Store and SBERT Index
│   ├── generation/           # Grounded Generator and Safety Guard
│   ├── escalation/           # Hybrid Escalation Engine
│   └── evaluation/           # LLM Judge and Evaluation Harness
├── scripts/                  # Reproducible Pipeline Scripts
├── evaluation/               # Golden Set and Annotation Queue
├── artifacts/                # Metrics, Failure Analysis, and Logs
├── tests/                    # Pytest Suite
└── docs/                     # Detailed Engineering Documentation
```

## Testing
Run the full test suite to verify core module stability:
```bash
pytest -q
```

## Limitations
-   **Domain Specificity**: The current system is optimized for AmazonHelp and may require taxonomy retraining for other brands.
-   **Context Window**: The system handles single-thread conversations; multi-day context is not currently supported.
-   **Temporal Drift**: The retrieval corpus is static and does not prioritize the most recent support policies.
