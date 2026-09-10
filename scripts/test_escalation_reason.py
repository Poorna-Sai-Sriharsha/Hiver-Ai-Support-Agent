from unittest.mock import MagicMock

from src.escalation.escalation_system import EscalationSystem


def test_reasoning():
    mock_llm = MagicMock()
    config = {
        'brand': {'name': 'AmazonHelp'},
        'prompts': {'escalation_reasoning': "Prompt"}
    }
    esc = EscalationSystem(mock_llm, config)
    
    # Scenario: Signal triggers escalation, but LLM says AUTO_HANDLED
    mock_llm.call.return_value = '{"decision": "AUTO_HANDLED", "reason": "LLM thinks it is fine"}'
    
    # Low retrieval score (0.1) triggers escalation
    res = esc.decide("Where is my order?", "Reply", 0.1, "Order & Logistics")
    
    print(f"Decision: {res['decision']}")
    print(f"Reason: {res['reason']}")
    if res['decision'] == "ESCALATED" and res['reason'] == "LLM thinks it is fine":
        print("RESULT: BUG FOUND - Signal triggered escalation but LLM reason was used.")
    else:
        print("RESULT: No bug found.")

if __name__ == "__main__":
    test_reasoning()
