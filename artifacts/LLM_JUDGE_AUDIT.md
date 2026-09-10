# LLM Judge Audit

## Rubric Review
- **Dimensions**: 7 dimensions (Relevance, Correctness, Groundedness, Helpfulness, Tone, Safety, Completeness).
- **Scale**: 0-4.
- **Input Coverage**: The judge sees the customer message, context, generated reply, evidence, and expected points. This is a high-quality input set.

## Potential Biases & Weaknesses
- **Score Inflation**: The rubric defines the scale but doesn't provide anchor examples (few-shot). LLMs are notorious for "central tendency bias" or inflation, often avoiding 0s and 1s.
- **Consistency**: There is no implementation of multi-judge voting or repeated runs to ensure the score is stable.
- **Grounding Loop**: The judge is asked to check groundedness, but if the judge itself is an LLM, it might "hallucinate" that a response is grounded simply because it looks plausible.

## Conclusion
The judge is well-structured but lacks the calibration required for high-precision evaluation. It should be augmented with anchor examples and a consistency check.
