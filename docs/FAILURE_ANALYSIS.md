# Failure Analysis Report

This document categorizes and analyzes the systematic failures of the Hiver AI Support Agent prototype discovered during evaluation on the test set.

## Summary of Failure Modes

| Failure Mode | Frequency | Impact Area | Root Cause |
|---|---|---|---|
| Overlapping Intents | 12 | Classification | Multi-intent messages causing trigger collisions. |
| Insufficient Evidence | 8 | Retrieval | Specific model-based evidence missing from the knowledge base. |
| Sarcasm Misinterpretation | 5 | Escalation | Literal interpretation of sarcastic positive markers. |
| Ambiguous Messages | 15 | Classification | Lack of context leading to probabilistic guessing. |
| Outdated Responses | 7 | Retrieval | Absence of temporal weighting in retrieval. |

---

## Detailed Analysis

### 1. Overlapping Intents
- **Description**: Messages containing multiple requests (e.g., "late delivery" AND "refund request").
- **Representative Example**: "My package is late and I want a refund."
- **Expected Behavior**: Classify as "Refunds & Returns" (Higher priority).
- **Actual Behavior**: Classified as "Delivery & Shipping".
- **Root Cause**: The classifier identified the first detected trigger ("late") and stopped, failing to recognize the user's primary goal (the refund).
- **Mitigation**: Implement multi-label classification or a priority-based hierarchy for intents.

### 2. Insufficient Retrieval Evidence
- **Description**: Retrieval of generic guides when a specific, model-dependent answer is required.
- **Representative Example**: "How do I activate my specific Amazon Kindle Oasis 3rd Gen in India?"
- **Expected Behavior**: Provide specific steps for the Kindle Oasis 3rd Gen.
- **Actual Behavior**: Provided a generic Kindle activation guide.
- **Root Cause**: The vector store retrieved the most similar general guides, but the specific technical manual for that model was absent from the training set.
- **Mitigation**: Expand the retrieval corpus with more granular technical documentation.

### 3. Sarcasm Misinterpretation
- **Description**: Failure to detect negative sentiment expressed through sarcastic positive language.
- **Representative Example**: "Wow, thanks for delivering my package to my neighbor's roof! Great job!"
- **Expected Behavior**: Escalate to human review (Severe Complaint).
- **Actual Behavior**: Auto-handled as a "General Inquiry".
- **Root Cause**: The LLM interpreted "thanks" and "Great job" literally, missing the environmental context of the delivery failure.
- **Mitigation**: Integrate explicit sentiment analysis signals into the escalation engine.

### 4. Ambiguous Customer Messages
- **Description**: Short, context-less messages that provide no semantic triggers.
- **Representative Example**: "It's not working."
- **Expected Behavior**: Trigger a "Clarification" request.
- **Actual Behavior**: Classified as "Product Quality".
- **Root Cause**: Lack of context forced the classifier to guess based on the global distribution of intents in the dataset.
- **Mitigation**: Implement a dedicated "Clarification" intent for messages with low semantic density.

### 5. Outdated Historical Responses
- **Description**: Retrieval of obsolete policies or procedures from old interactions.
- **Representative Example**: "How do I use the old Kindle Fire app?"
- **Expected Behavior**: Inform the user that the app is deprecated.
- **Actual Behavior**: Provided instructions for the deprecated app.
- **Root Cause**: The vector store treats all historical interactions as equally valid regardless of age.
- **Mitigation**: Implement temporal weighting (time-decay) on retrieval scores to prioritize recent resolutions.
