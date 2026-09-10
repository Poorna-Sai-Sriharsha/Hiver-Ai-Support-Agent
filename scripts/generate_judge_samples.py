import sys
import os
sys.path.append(os.getcwd())

import pandas as pd
import json
import logging
from src.agent import SupportAgent
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_samples():
    test_path = 'data/processed/test.csv'
    train_path = 'data/processed/train.csv'
    config_path = 'config/config.yaml'
    output_path = 'artifacts/evaluation_results.json'
    
    if not os.path.exists(test_path):
        logger.error("Test set not found.")
        return

    logger.info("Loading data...")
    test_df = pd.read_csv(test_path)
    train_df = pd.read_csv(train_path)
    
    # Index the VectorStore
    kb = VectorStore()
    kb.index_data(train_df)
    
    agent = SupportAgent(config_path, kb, LLMClient())
    
    # Sample 60 examples from the test set for judging
    sample_df = test_df.sample(min(60, len(test_df)), random_state=42)
    
    results = []
    logger.info(f"Generating responses for {len(sample_df)} samples...")
    
    for _, row in sample_df.iterrows():
        text = row['customer_message']
        context = ""
        
        res = agent.process_message(text, context)
        
        results.append({
            "original_message": text,
            "reply": res['reply'],
            "evidence": res['evidence'],
            "intent": res['intent'],
            "escalation": res['escalation']
        })
    
    os.makedirs("artifacts", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
    
    logger.info(f"Successfully generated {len(results)} judge samples at {output_path}")

if __name__ == "__main__":
    generate_samples()
