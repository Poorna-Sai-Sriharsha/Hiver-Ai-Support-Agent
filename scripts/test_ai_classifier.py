import logging

import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

from src.agent import SupportAgent
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_classifier():
    gs_path = 'evaluation/golden_set.csv'
    df = pd.read_csv(gs_path)

    # Setup Agent
    kb = VectorStore()
    # Load index if exists, else build
    try:
        kb.load('data/vector_index.pkl')
    except:
        # If no index, just load train data for the test
        import os
        if os.path.exists('data/processed/train.csv'):
            train_df = pd.read_csv('data/processed/train.csv')
            kb.index_data(train_df)

    agent = SupportAgent("config/config.yaml", kb, LLMClient())

    preds = []
    for text in df['customer_message']:
        res = agent.process_message(text)
        preds.append(res['intent'])

    acc = accuracy_score(df['gold_intent'], preds)
    f1 = f1_score(df['gold_intent'], preds, average='macro')

    logger.info(f"AI Classifier Results: Acc={acc:.4f}, F1={f1:.4f}")
    return acc, f1

if __name__ == "__main__":
    evaluate_classifier()
