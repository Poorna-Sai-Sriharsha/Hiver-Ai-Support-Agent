from unittest.mock import MagicMock

import pytest

from src.generation.ai_generator import AIResponseGenerator


@pytest.fixture
def mock_config():
    return {
        'brand': {'name': 'AmazonHelp'},
        'prompts': {
            'reply_generation': "Brand: {brand}, Context: {context}, Text: {text}"
        }
    }

def test_generation_basic_flow(mock_config):
    mock_llm = MagicMock()
    mock_llm.call.return_value = "Your order is on the way."
    generator = AIResponseGenerator(mock_llm, mock_config)

    evidence = [{'customer_message': 'Where is it?', 'brand_response': 'On the way', 'tweet_id': '1'}]
    res = generator.generate("Where is my order?", "", evidence)

    assert "Your order is on the way" in res['reply']
    assert 'evidence_ids' in res

def test_grounding_failure(mock_config):
    mock_llm = MagicMock()
    # First call: generate reply
    # Second call: extract claims
    # Third+ calls: verify claims
    mock_llm.call.side_effect = [
        "Your order will arrive on Friday.", # reply
        '["Your order will arrive on Friday"]', # claims
        '{"status": "UNSUPPORTED", "reason": "No date in evidence"}' # verify
    ]
    generator = AIResponseGenerator(mock_llm, mock_config)

    evidence = [{'customer_message': 'Where is it?', 'brand_response': 'Checking now', 'tweet_id': '1'}]
    res = generator.generate("Where is my order?", "", evidence)

    assert res['grounding_score'] == 0.0
    assert res['grounding_details'][0]['status'] == 'UNSUPPORTED'
