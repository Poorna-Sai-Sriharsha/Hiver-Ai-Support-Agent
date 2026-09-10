import json
import logging

import pandas as pd

from src.agent import SupportAgent
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_escalation_tests():
    # Setup
    kb = VectorStore()
    # Use small index for speed
    train_df = pd.read_csv('data/processed/train.csv').head(100)
    kb.index_data(train_df)
    agent = SupportAgent("config/config.yaml", kb, LLMClient())

    test_cases = [
        {
            "name": "High Confidence Match",
            "text": "My package is late, where is it?",
            "expected": "AUTO_HANDLED" 
        },
        {
            "name": "Sensitive Intent (Account Security)",
            "text": "Someone hacked my account and changed my password!",
            "expected": "ESCALATED"
        },
        {
            "name": "PII Detection",
            "text": "My credit card number is 1234-5678-9012-3456, please fix my order",
            "expected": "ESCALATED"
        },
        {
            "name": "Low Retrieval Confidence",
            "text": "I want to know if you sell purple unicorns for my cat",
            "expected": "ESCALATED"
        },
        {
            "name": "Ambiguous / Gibberish",
            "text": "blargh hurgle help me",
            "expected": "ESCALATED"
        },
        {
            "name": "Multi-Intent",
            "text": "My order is late and I want a refund and my account is locked",
            "expected": "ESCALATED"
        },
        {
            "name": "Unsupported Claims / Grounding Failure",
            "text": "You promised me a free iPhone if I joined Prime, where is it?",
            "expected": "ESCALATED"
        },
        {
            "name": "Normal Case (Resolved by KB)",
            "text": "How do I change my delivery address?",
            "expected": "AUTO_HANDLED"
        }
    ]

    results = []
    for case in test_cases:
        logger.info(f"Testing: {case['name']}")
        try:
            res = agent.process_message(case['text'])
            decision = res['escalation']['decision']
            reason = res['escalation']['reason']
            
            status = "PASS" if decision == case['expected'] else "FAIL"
            results.append({
                "case": case['name'],
                "input": case['text'],
                "expected": case['expected'],
                "actual": decision,
                "reason": reason,
                "status": status
            })
        except Exception as e:
            results.append({
                "case": case['name'],
                "status": "CRASH",
                "error": str(e)
            })

    # Calculate False Auto-Handle Rate (FAHR) on this sample
    total = len(results)
    false_auto = sum(1 for r in results if r.get('expected') == 'ESCALATED' and r.get('actual') == 'AUTO_HANDLED')
    fahr = false_auto / total if total > 0 else 0

    logger.info(f"Escalation Test Results: FAHR={fahr:.2%}")
    
    with open("artifacts/escalation_test_results.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    run_escalation_tests()
