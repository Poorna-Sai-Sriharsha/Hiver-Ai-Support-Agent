# Interviewer Attack Readiness Report

## Critical Vulnerabilities

### 1. The "Fake" Dashboard
**Question**: "I see the dashboard shows a Macro-F1 of 0.91. Can you show me the code that calculates this number in real-time?"
**Evidence**: `app.py:57` hard-codes the value `"0.91"`. The metrics are not computed from the current agent; they are static strings.
**Verdict**: EXPOSED.

### 2. The "Mock" Agent
**Question**: "I'll enter a very specific query into the Live Agent. Why is it giving me a generic 'looking into your issue' response regardless of what I type?"
**Evidence**: `app.py:20-26` defines a `MockLLM` that returns generic responses for everything. The `SupportAgent` in the app is initialized with this `MockLLM`, not the real `LLMClient`.
**Verdict**: EXPOSED.

### 3. The "Synthetic" Golden Set
**Question**: "How did you ensure the 200 human labels in the golden set are unbiased?"
**Evidence**: `evaluation/golden_set.csv` contains the note "Simulated human label based on taxonomy" for every row.
**Verdict**: EXPOSED.

### 4. The "Missing" Validation
**Question**: "Can you show me the human-agreement scores for your LLM judge?"
**Evidence**: `evaluation/human_scores.csv` is missing from the repo. `scripts/validate_judge.py` cannot run.
**Verdict**: EXPOSED.

### 5. The "Broken" Pipeline
**Question**: "If I run your setup instructions from the README, why does `scripts/build_index.py` fail?"
**Evidence**: The file `scripts/build_index.py` does not exist in the repository.
**Verdict**: EXPOSED.

## Summary of Defensibility
The current implementation is a "prototype facade." It is designed to look finished and high-performing on the surface, but the underlying engineering is incomplete, and the metrics are fabricated/hard-coded in the UI. It would not survive a 5-minute technical deep-dive.
