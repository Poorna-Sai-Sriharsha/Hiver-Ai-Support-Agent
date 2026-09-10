# Analysis of Headline Metrics

This document provides a critical evaluation of the system's reported performance metrics, explaining why headline numbers may be misleading and identifying the limitations of the current evaluation harness.

## Reported Metric: Macro-F1 (Intent Classification)

The system reports a Macro-F1 score (to be finalized upon human labeling). In previous iterations, this was observed around 0.90.

### Why this number is misleading:

1.  **Brand-Specific Bias**: The performance is measured exclusively on **AmazonHelp**. Amazon's support interactions are highly standardized. Performance may drop significantly on brands with less structured data or more complex technical domains.
2.  **Class Imbalance**: The "Delivery & Shipping" intent dominates the dataset. High accuracy in this majority class can inflate overall metrics if not carefully analyzed via Macro-averaging (which we use, but it still reflects the specific nature of Amazon's queries).
3.  **Ambiguity in Ground Truth**: Twitter data is noisy. Some "correct" labels in the golden set are based on ambiguous messages where multiple intents are plausible.
4.  **Retrieval Overlap**: While we use conversation-level splitting, similar queries from different users can appear in both the train and test sets. This "semantic leakage" can make the model appear more capable of generalization than it is.

## Evaluation Limitations

### 1. LLM-as-a-Judge Limitations
The response quality is measured using an LLM judge. While useful for scale, this is not ground truth:
-   **Verbosity Bias**: LLMs tend to score longer, more polite responses higher, even if they are less accurate.
-   **Self-Preference**: LLMs may favor responses that mimic their own generation style.
-   **Rubric Drift**: The judge may interpret a "3" (Good) differently across different sessions.

### 2. Human Validation Sample Size
Human agreement is validated on a small sample (40-60 responses). While statistically indicative, this sample size is insufficient to capture the full variance of the agent's failure modes.

### 3. Offline vs. Online Performance
The evaluation is performed "offline" on a frozen dataset. In a live production environment:
-   **Temporal Drift**: Support policies change over time.
-   **Context Loss**: Real users may provide context across multiple days, whereas our prototype focuses on single-thread reconstructions.

## Conclusion
The reported metrics should be viewed as a **performance ceiling** under optimized, offline conditions. They demonstrate the prototype's capability to generalize from historical data but do not guarantee identical performance in a live, multi-turn production environment.
