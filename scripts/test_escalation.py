from unittest.mock import MagicMock

from src.escalation.escalation_system import EscalationSystem


def test_policy():
    mock_llm = MagicMock()
    config = {
        'brand': {'name': 'AmazonHelp'},
        'prompts': {'escalation_reasoning': "Prompt {brand} {text} {reply}"}
    }
    esc = EscalationSystem(mock_llm, config)
    
    tests = [
        # (text, reply, retrieval_score, intent, expected_decision, description)
        ("Where is my order?", "It is late.", 0.1, "Order & Logistics", "ESCALATED", "Low retrieval score"),
        ("I want to sue you", "Sorry.", 0.8, "Order & Logistics", "ESCALATED", "Legal keyword"),
        ("My account is hacked", "Help is here.", 0.8, "Account & Security", "ESCALATED", "Sensitive intent"),
        ("Everything is fine", "Great.", 0.8, "General Inquiry", "AUTO_HANDLED", "Standard case"),
    ]
    
    # Mock LLM to return AUTO_HANDLED by default
    mock_llm.call.return_value = '{"decision": "AUTO_HANDLED", "reason": "No reason"}'
    
    print(f"{'Description':<30} | {'Expected':<12} | {'Actual':<12} | {'Result'}")
    print("-" * 70)
    
    for text, reply, score, intent, expected, desc in tests:
        res = esc.decide(text, reply, score, intent)
        actual = res['decision']
        print(f"{desc:<30} | {expected:<12} | {actual:<12} | {'PASS' if actual == expected else 'FAIL'}")

if __name__ == "__main__":
    test_policy()
