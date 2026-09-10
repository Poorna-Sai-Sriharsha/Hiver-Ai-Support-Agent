import logging
import os

import pandas as pd
from sklearn.metrics import cohen_kappa_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_judge(judge_results_path: str, human_results_path: str):
    """
    Compares LLM judge scores with human scores.
    """
    if not os.path.exists(judge_results_path) or not os.path.exists(human_results_path):
        logger.error("Results files missing.")
        return

    judge_df = pd.read_csv(judge_results_path)
    human_df = pd.read_csv(human_results_path)

    # Merge on example_id
    merged = pd.merge(judge_df, human_df, on='example_id', suffixes=('_llm', '_human'))

    metrics = {}
    for dim in ['relevance', 'correctness', 'groundedness', 'helpfulness', 'tone', 'safety', 'completeness']:
        llm_scores = merged[f'{dim}_llm']
        human_scores = merged[f'{dim}_human']

        # Exact agreement
        agreement = (llm_scores == human_scores).mean()
        # Within-1 agreement
        within_one = (abs(llm_scores - human_scores) <= 1).mean()
        # Weighted Kappa
        kappa = cohen_kappa_score(human_scores, llm_scores, weights='linear')

        metrics[dim] = {
            "exact_agreement": agreement,
            "within_one_agreement": within_one,
            "weighted_kappa": kappa
        }

    # Save results
    with open("evaluation/JUDGE_VALIDATION.md", "w") as f:
        f.write("# Judge Validation Report\n\n")
        f.write("## Overview\n")
        f.write("Comparing LLM Judge scores against a human-reviewed subset (40-60 examples).\n\n")
        f.write("## Agreement Metrics\n")
        f.write("| Dimension | Exact Agreement | Within-1 Agreement | Weighted Kappa |\n")
        f.write("|---|---|---|---|\n")
        for dim, m in metrics.items():
            f.write(f"| {dim} | {m['exact_agreement']:.2%} | {m['within_one_agreement']:.2%} | {m['weighted_kappa']:.2f} |\n")

    logger.info("Judge validation complete. Results saved to evaluation/JUDGE_VALIDATION.md")

if __name__ == "__main__":
    validate_judge("artifacts/judge_scores.csv", "evaluation/human_scores.csv")
