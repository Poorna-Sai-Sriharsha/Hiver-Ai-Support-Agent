# Safety / PII Report

## PII Detection
- **Test**: Verified `SafetyGuard` against emails, phone numbers, order IDs, and inappropriate language.
- **Result**: PASS. The regex-based patterns correctly identify and block responses containing PII or bad words.

## Hallucination Filter
- **Test**: Checked the numerical hallucination filter (numbers > 3 digits).
- **Result**: PASS (Functionally), but HIGH False Positive risk.
- **Observation**: Any number like "1234" not in the evidence will trigger a safety violation. This is too aggressive for real-world use (e.g., order IDs, dates).

## Prompt Injection
- **Test**: Attempted system prompt reveal and historical data extraction.
- **Result**: PASS (in Mock mode).
- **Observation**: The system lacks an explicit "Input Guard" to detect injections *before* they reach the LLM. It relies entirely on the LLM's own robustness and the output-side `SafetyGuard`.

## Conclusion
The output-side safety is robust for simple PII. The hallucination filter is too crude. The system is potentially vulnerable to sophisticated prompt injections that might bypass the LLM's internal safety but could be caught by the `SafetyGuard` if they produce PII in the output.
