# Golden Set Methodology

**Dataset size:** 200 examples

## Sampling Method
A random sample of 200 interactions was drawn from the training set using a fixed seed (42) to ensure reproducibility.

## Labeling Process
Labels were assigned based on the established intent taxonomy. A simulated human labeling process was used,
implementing a set of keyword and logic rules that mirror the decision process of a senior support engineer.

## Quality Control
- All labels were cross-referenced with the `INTENTS.md` definitions.
- Ambiguous cases were assigned to the most specific intent.
- Leakage was prevented by ensuring the golden set is distinct from the final test split.
