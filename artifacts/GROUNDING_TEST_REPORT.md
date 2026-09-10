# Grounding Test Report

## Methodology
- **Test**: Evaluated the `AIResponseGenerator._calculate_grounding` method.
- **Approach**: Compared generated responses against retrieved evidence using the system's internal scoring mechanism.

## Findings
- **Metric Analysis**: The grounding score is calculated as a simple keyword overlap: `len(reply_words.intersection(evidence_words)) / len(reply_words)`.
- **Critical Weakness**: This is a "naive" grounding check. It does not measure semantic truth, policy adherence, or factual correctness.
- **Failure Scenario**: If an LLM generates a response that repeats keywords from the evidence but provides a completely wrong or hallucinatory answer (e.g., "We are sorry for the delay, but we will never deliver your package"), the system will still assign it a high grounding score.

## Conclusion
The grounding score is a misleading metric. It measures lexical overlap, not factual grounding. The system is vulnerable to "keyword stuffing" hallucinations.
