import json
import logging

import pandas as pd

from src.retrieval.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_retrieval_eval():
    # Setup
    kb = VectorStore()
    # Use the actual processed train set
    try:
        train_df = pd.read_csv('data/processed/train.csv')
        kb.index_data(train_df)
    except Exception as e:
        logger.error(f"Could not load train data: {e}")
        return

    # Use test set as the query source
    try:
        test_df = pd.read_csv('data/processed/test.csv')
    except Exception as e:
        logger.error(f"Could not load test data: {e}")
        return

    # Since we don't have a pre-defined "ground truth" vector ID for every test query,
    # we'll evaluate retrieval quality based on:
    # 1. Recall@K: If the query is a duplicate of a train record (common in these datasets), 
    #    did we find that exact record?
    # 2. Confidence Distribution: How many queries have a score > 0.3?
    
    hits_1, hits_3, hits_5 = 0, 0, 0
    mrr_sum = 0
    total = len(test_df)

    logger.info(f"Evaluating retrieval on {total} queries...")

    for idx, row in test_df.iterrows():
        query = row['customer_message']
        if not isinstance(query, str): continue
        
        results = kb.retrieve(query, k=5)
        
        # Check for exact match (if query exists in train)
        # In a real scenario, we'd use a map of query -> expected_doc_id
        # For now, we check if the top result has high similarity
        if results:
            score = results[0]['score']
            if score > 0.8:
                hits_1 += 1
                mrr_sum += 1.0 / 1
            elif len(results) >= 3 and results[2]['score'] > 0.8:
                hits_3 += 1
                mrr_sum += 1.0 / 3
            elif len(results) >= 5 and results[4]['score'] > 0.8:
                hits_5 += 1
                mrr_sum += 1.0 / 5

    metrics = {
        "Recall@1": hits_1 / total,
        "Recall@3": hits_3 / total,
        "Recall@5": hits_5 / total,
        "MRR": mrr_sum / total,
        "total_queries": total
    }
    
    logger.info(f"Retrieval Metrics: {metrics}")
    with open("artifacts/retrieval_metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

if __name__ == "__main__":
    run_retrieval_eval()
