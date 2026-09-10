# Golden Set Forensic Audit

## Claim Verification
- **Claim**: "200 interactions with human-like labels."
- **Finding**: The labels are NOT hand-labelled.
- **Evidence**: The `annotator_notes` column in `evaluation/golden_set.csv` explicitly states: **"Simulated human label based on taxonomy."** for every single example.

## Label Authenticity
- **Status**: FAKE / SIMULATED.
- **Mechanism**: Labels were automatically generated to match the project's own intent taxonomy.
- **Impact**: The evaluation metrics (Accuracy, F1) are likely inflated and misleading because the system is being tested against labels that were derived from the same logic it uses to classify.

## Label Quality
- **Consistency**: The labels are perfectly consistent with the taxonomy because they were generated from it.
- **Realism**: They lack the noise, ambiguity, and error typical of genuine human annotation.

## Conclusion
The claim of human-labelled data is false. The golden set is a synthetic benchmark. This significantly undermines the validity of the reported performance metrics.
