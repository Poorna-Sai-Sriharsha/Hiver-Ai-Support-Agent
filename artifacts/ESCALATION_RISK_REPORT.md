# Escalation Risk Report

## False Auto-Handle Analysis
- **Metric**: False Auto-Handle Rate = 4.5% (9 cases out of 200).
- **Finding**: The system occasionally fails to escalate high-severity cases, potentially providing an automated response to a user who should have been handled by a human.

## High-Risk Failures
1. **Fraud/Legal Accusations**: Cases where users mention "cheated" or "internal pricing error" are sometimes auto-handled.
2. **Account Access Nightmares**: Complex account closure issues that are flagged as "Yes" for escalation in the golden set are sometimes missed by the agent.

## Root Cause Analysis
- **Signal Weakness**: The measurable signals (retrieval score, keywords) may be too lenient.
- **LLM Over-Confidence**: The LLM reasoner may be incorrectly classifying nuanced frustration as "standard" instead of "escalation-worthy".

## Conclusion
A 4.5% false auto-handle rate is moderately risky. For a production support system, the cost of a "False Auto-Handle" (giving a robotic response to an angry/fraud-accusing customer) is much higher than a "False Escalation".
