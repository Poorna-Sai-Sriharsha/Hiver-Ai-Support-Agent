import logging
import os

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sample_for_annotation(n=200, seed=42):
    # CRITICAL FIX: Sample from TEST set, NOT TRAIN set, to prevent data leakage.
    test_path = 'data/processed/test.csv'
    output_path = 'evaluation/annotation_queue.csv'

    if not os.path.exists(test_path):
        logger.error(f"Test data not found at {test_path}")
        return

    df = pd.read_csv(test_path)

    # We only want examples that have a customer message and a brand response
    df = df.dropna(subset=['customer_message', 'historical_brand_response'])

    # Reproducible sampling
    np.random.seed(seed)
    sampled_df = df.sample(n=min(n, len(df)))

    # Keep only necessary columns for the annotator to avoid clutter
    # and preserve IDs for provenance.
    cols_to_keep = ['tweet_id', 'conversation_id', 'customer_message', 'historical_brand_response']
    existing_cols = [c for c in cols_to_keep if c in sampled_df.columns]
    sampled_df = sampled_df[existing_cols]

    # Add annotation columns
    sampled_df['gold_intent'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['should_escalate'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['escalation_reason'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['severity'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['expected_response_points'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['annotation_confidence'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['annotator_notes'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['annotation_timestamp'] = "WAITING_FOR_HUMAN_ANNOTATION"
    sampled_df['is_annotated'] = False

    os.makedirs('evaluation', exist_ok=True)
    sampled_df.to_csv(output_path, index=False)
    logger.info(f"Sampled {len(sampled_df)} examples from TEST set to {output_path}")

if __name__ == "__main__":
    sample_for_annotation()
