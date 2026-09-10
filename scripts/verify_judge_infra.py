import json
import logging

from src.evaluation.llm_judge import LLMJudge
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_judge_verification():
    llm = LLMClient()
    judge = LLMJudge(llm)
    
    test_cases = [
        {
            "name": "Valid JSON Response",
            "mock_response": '{"relevance": 4, "correctness": 4, "groundedness": 4, "helpfulness": 4, "tone": 4, "safety": 4, "completeness": 4, "reasoning": "Perfect response."}'
        },
        {
            "name": "Malformed JSON",
            "mock_response": '{"relevance": 4, "correctness": "High", "reasoning": "Wrong type"}'
        },
        {
            "name": "Markdown Blocked JSON",
            "mock_response": '```json\n{"relevance": 3, "correctness": 3, "groundedness": 3, "helpfulness": 3, "tone": 3, "safety": 3, "completeness": 3, "reasoning": "Good."}\n```'
        },
        {
            "name": "Empty Response",
            "mock_response": ''
        }
    ]
    
    results = []
    for case in test_cases:
        logger.info(f"Testing Judge: {case['name']}")
        # We patch the llm.call to return the mock response
        llm.call = lambda x: case['mock_response']
        
        try:
            score = judge.judge("query", "ctx", "reply", [], "points")
            if score['relevance'] == 0 and "Judge Error" in score['reasoning']:
                status = "CAUGHT_ERROR" if case['name'] != "Valid JSON Response" else "FAIL"
            elif case['name'] == "Valid JSON Response" and score['relevance'] == 4 or case['name'] == "Markdown Blocked JSON" and score['relevance'] == 3:
                status = "PASS"
            else:
                status = "UNEXPECTED"
            
            results.append({"case": case['name'], "status": status, "score": score})
        except Exception as e:
            results.append({"case": case['name'], "status": "CRASH", "error": str(e)})

    with open("artifacts/judge_infra_results.json", "w") as f:
        json.dump(results, f, indent=4)
    logger.info("Judge infrastructure verification complete.")

if __name__ == "__main__":
    run_judge_verification()
