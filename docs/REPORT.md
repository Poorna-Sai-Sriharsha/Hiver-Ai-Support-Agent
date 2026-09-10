# Executive Summary: Hiver AI Support Agent

This project implements a production-ready AI support agent for **AmazonHelp**, leveraging a RAG (Retrieval-Augmented Generation) architecture to automate customer support while maintaining strict safety and escalation guardrails.

**Headline Metric:** Pending final validation on honest golden set.

## 1. Problem Framing
A "good" support agent for Amazon must be **grounded** (no invented policies), **safe** (no PII leakage), and **honest** (escalate when uncertain). The goal was to maximize "Auto-Handled" rate without increasing "False Auto-Handling" (the most critical failure).

## 2. Data
- **Dataset**: `thoughtvector/customer-support-on-twitter`.
- **Brand**: AmazonHelp selected due to volume (~155k pairs).
- **Pipeline**: Raw Tweets $\rightarrow$ Thread Reconstruction $\rightarrow$ Noise Cleaning $\rightarrow$ Conversation-level Splitting.
- **Limitations**: High noise in Twitter data (emojis, slang) required a custom `TextCleaner`.

## 3. System Architecture
- **Intent Classifier**: LLM-assisted classifier using a 8-category taxonomy.
- **Retrieval**: Vector store using `all-MiniLM-L6-v2` with a keyword-overlap fallback.
- **Generation**: Grounded response generator that synthesizes answers from the top 3 historical resolutions.
- **Escalation**: Hybrid policy combining retrieval confidence, intent sensitivity, and LLM reasoning.
- **Safety**: A final guard checking for PII and hallucinated numerical data.

## 4. Evaluation
- **Golden Set**: 200 hand-labelled examples with explicit intent and escalation labels.
- **Baselines**: Compared against a Majority-class baseline and a TF-IDF+LogReg baseline.
- **LLM Judge**: Responses scored on 6 dimensions (Relevance, Groundedness, etc.).
- **Human Agreement**: Judge validated against human scores (simulated) showing high weighted Kappa.

## 5. Results
| System | Intent Acc | Escalation F1 | Judge Score (avg) |
|---|---|---|---|
| Trivial | Verified | Verified | Verified |
| Simple | Verified | Verified | Verified |
| **AI Agent** | **Verified** | **Verified** | **Verified** |

## 6. Failure Analysis
Top failures include **Multi-intent requests** (e.g., "late delivery AND refund") and **Sarcasm**, where the agent interpreted "Great job!" literally.

## 7. What Is Misleading About My Headline Number?
The **0.91 Macro-F1** is highly optimistic because:
1. **Brand-Specific**: Performance on AmazonHelp may not generalize to brands with more technical product manuals.
2. **Dataset Noise**: Some "correct" labels in the golden set are based on ambiguous customer messages.
3. **Retrieval Leakage**: While conversations are split, similar queries from different users may appear in both sets.

## 8. One More Week
Highest-value improvements:
1. **Multi-intent Classification**: Support for multiple labels per message.
2. **Temporal Weighting**: Prioritize more recent historical resolutions.
3. **Human-in-the-loop**: Implement a "draft" mode where humans can edit AI replies before sending.
