import sys
import os
sys.path.append(os.getcwd())

import json
import logging
import pandas as pd
from src.evaluation.llm_judge import LLMJudge
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_ai_judge():
    results_path = 'artifacts/evaluation_results.json'
    output_path = 'artifacts/ai_judge_scores.json'
    
    if not os.path.exists(results_path):
        logger.error("No evaluation results found to judge.")
        return

    with open(results_path, 'r') as f:
        samples = json.load(f)
    
    llm = LLMClient()
    judge = LLMJudge(llm)
    
    ai_scores = []
    logger.info(f"AI Judging {len(samples)} samples...")
    
    for i, sample in enumerate(samples):
        # Test set samples don't have 'expected_points'
        score = judge.judge(
            customer_message=sample['original_message'],
            context="",
            reply=sample['reply'],
            evidence=sample['evidence'],
            expected_points="N/A (Test Set Sample)"
        )
        
        ai_scores.append({
            "example_id": i,
            "scores": score
        })
        if (i + 1) % 10 == 0:
            logger.info(f"Judged {i+1}/{len(samples)}...")

    with open(output_path, 'w') as f:
        json.dump(ai_scores, f, indent=4)
    
    logger.info(f"AI judge scores saved to {output_path}")

if __name__ == "__main__":
    run_ai_judge()
