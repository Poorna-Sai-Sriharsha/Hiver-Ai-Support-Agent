from unittest.mock import MagicMock

import pytest

from src.intent.ai_classifier import AIIntentClassifier


@pytest.fixture
def mock_config():
    return {
        'brand': {'name': 'AmazonHelp'},
        'intents': ['Delivery & Shipping', 'Refunds & Returns', 'Account & Security'],
        'prompts': {
            'intent_classification': "Brand: {brand}, Intents: {intents}, Text: {text}"
        }
    }

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    return llm

def test_classifier_basic_flow(mock_llm, mock_config):
    classifier = AIIntentClassifier(mock_llm, mock_config)
    mock_llm.call.return_value = '{"intent": "Delivery & Shipping", "confidence": 0.9, "reason": "Keywords", "alternative_intents": []}'

    res = classifier.classify("Where is my package?")
    assert res['intent'] == "Delivery & Shipping"
    assert res['confidence'] == 0.9

def test_classifier_malformed_json(mock_llm, mock_config):
    classifier = AIIntentClassifier(mock_llm, mock_config)
    mock_llm.call.return_value = "This is not JSON"

    res = classifier.classify("Hello")
    assert res['intent'] == "General Inquiry" # Fallback
    assert res['confidence'] == 0.0

def test_classifier_confidence_parsing(mock_llm, mock_config):
    classifier = AIIntentClassifier(mock_llm, mock_config)
    # Test "high" -> 0.9
    mock_llm.call.return_value = '{"intent": "Delivery & Shipping", "confidence": "high", "reason": "...", "alternative_intents": []}'
    res = classifier.classify("Test")
    assert res['confidence'] == 0.9
