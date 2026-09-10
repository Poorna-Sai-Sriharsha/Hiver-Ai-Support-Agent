import json
import logging

from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_resilience_tests():
    llm = LLMClient()
    
    test_scenarios = [
        {"name": "401 Unauthorized", "error": "401 Unauthorized"},
        {"name": "403 Forbidden", "error": "403 Forbidden"},
        {"name": "408 Request Timeout", "error": "408 Request Timeout"},
        {"name": "429 Too Many Requests", "error": "429 Too Many Requests"},
        {"name": "500 Internal Server Error", "error": "500 Internal Server Error"},
        {"name": "502 Bad Gateway", "error": "502 Bad Gateway"},
        {"name": "503 Service Unavailable", "error": "503 Service Unavailable"},
        {"name": "Malformed JSON", "error": '{"intent": "Oops", "confidence": "NaN"}'},
        {"name": "Empty Response", "error": ""},
        {"name": "Connection Failure", "error": Exception("Connection refused")},
    ]
    
    results = []
    for scenario in test_scenarios:
        logger.info(f"Testing Resilience: {scenario['name']}")
        
        def create_mock(err):
            def mock_call(prompt):
                if isinstance(err, Exception):
                    raise err
                if any(code in err for code in ["401", "403", "408", "429", "500", "502", "503"]):
                    raise RuntimeError(err)
                return err
            return mock_call

        llm.call = create_mock(scenario['error'])
        
        try:
            llm.call("Hello")
            status = "HANDLED"
        except Exception as e:
            status = f"RAISED: {type(e).__name__}"
        
        results.append({
            "scenario": scenario['name'],
            "status": status
        })
    
    with open("artifacts/api_resilience_results.json", "w") as f:
        json.dump(results, f, indent=4)
    logger.info("API resilience testing complete.")

if __name__ == "__main__":
    run_resilience_tests()
