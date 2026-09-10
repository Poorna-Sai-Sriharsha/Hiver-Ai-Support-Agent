# Human vs Judge Validation Report

## Claim Verification
- **Claim**: "Validated against a hand-labelled golden set... with LLM-as-judge human-agreement audit."
- **Finding**: FAILED. No human scores are available in the repository.

## Evidence
- The script `scripts/validate_judge.py` exists, but the required input file `evaluation/human_scores.csv` is missing from the repository.
- Without this file, it is impossible to verify if the LLM judge's scores align with human judgment.

## Conclusion
The claim of human-judge agreement is unsupported by the current codebase. The evaluation relies entirely on the LLM judge without external validation.
