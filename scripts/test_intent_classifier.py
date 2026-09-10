import json
import logging

import pandas as pd

from src.agent import SupportAgent
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_classifier_tests():
    # Setup
    kb = VectorStore()
    # Minimal index
    train_df = pd.DataFrame({
        'customer_message': ["Help me with my order"],
        'historical_brand_response': ["We can help you"],
        'tweet_id': [1]
    })
    kb.index_data(train_df)
    agent = SupportAgent("config/config.yaml", kb, LLMClient())

    test_cases = [
        {"name": "Valid Message", "text": "Where is my package?", "expected_type": "VALID"},
        {"name": "Empty Message", "text": "", "expected_type": "HANDLED"},
        {"name": "Malformed Input", "text": None, "expected_type": "HANDLED"},
        {"name": "Typos", "text": "Wher is my pakage?", "expected_type": "VALID"},
        {"name": "Emojis", "text": "📦 Where is my order? 🚚", "expected_type": "VALID"},
        {"name": "Long Message", "text": "A" * 1000, "expected_type": "HANDLED"},
        {"name": "Ambiguous Input", "text": "I need help", "expected_type": "VALID"},
        {"name": "Multi-intent", "text": "My order is late and I want a refund", "expected_type": "VALID"},
        {"name": "Gibberish", "text": "asdfghjkl", "expected_type": "VALID"},
        {"name": "OOD Input", "text": "What is the weather in Tokyo?", "expected_type": "VALID"},
    ]

    results = []
    for case in test_cases:
        logger.info(f"Testing Classifier: {case['name']}")
        try:
            res = agent.process_message(case['text'])
            # We check if we got a valid intent string
            intent = res['intent']
            if isinstance(intent, str) and len(intent) > 0:
                actual = "VALID"
            else:
                actual = "INVALID"
            
            status = "PASS" if actual == case['expected_type'] or case['expected_type'] == "HANDLED" else "FAIL"
            results.append({
                "case": case['name'],
                "input": case['text'],
                "intent": intent,
                "status": status
            })
        except Exception as e:
            results.append({"case": case['name'], "status": "CRASH", "error": str(e)})

    with open("artifacts/classifier_test_results.json", "w") as f:
        json.dump(results, f, indent=4)
    logger.info("Classifier suite complete.")

if __name__ == "__main__":
    run_classifier_tests()
