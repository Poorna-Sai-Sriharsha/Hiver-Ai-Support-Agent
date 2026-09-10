from unittest.mock import MagicMock

import pytest

from src.escalation.escalation_system import EscalationSystem


@pytest.fixture
def mock_config():
    return {
        'brand': {'name': 'AmazonHelp'},
        'prompts': {
            'escalation_reasoning': "Brand: {brand}, Text: {text}, Reply: {reply}"
        }
    }

def test_escalation_low_retrieval(mock_config):
    mock_llm = MagicMock()
    mock_llm.call.return_value = '{"decision": "AUTO_HANDLED", "reason": "ok"}'
    esc = EscalationSystem(mock_llm, mock_config)

    # retrieval_score < 0.3 should trigger escalation
    res = esc.decide("Hello", "Hi", 0.2, "General Inquiry")
    assert res['decision'] == "ESCALATED"
    assert "low historical evidence" in res['reason']

def test_escalation_sensitive_intent(mock_config):
    mock_llm = MagicMock()
    mock_llm.call.return_value = '{"decision": "AUTO_HANDLED", "reason": "ok"}'
    esc = EscalationSystem(mock_llm, mock_config)

    res = esc.decide("I want to sue", "Sorry", 0.9, "Severe Complaint / Fraud")
    assert res['decision'] == "ESCALATED"
    assert "sensitive intent category" in res['reason']

def test_escalation_llm_trigger(mock_config):
    mock_llm = MagicMock()
    mock_llm.call.return_value = '{"decision": "ESCALATED", "reason": "Nuanced issue"}'
    esc = EscalationSystem(mock_llm, mock_config)

    res = esc.decide("Hello", "Hi", 0.9, "General Inquiry")
    assert res['decision'] == "ESCALATED"
    assert "LLM reasoning: Nuanced issue" in res['reason']
