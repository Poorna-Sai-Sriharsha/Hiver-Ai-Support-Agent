from unittest.mock import MagicMock

from src.intent.ai_classifier import AIIntentClassifier


def test_mapping():
    mock_llm = MagicMock()
    config = {
        'brand': {'name': 'AmazonHelp'},
        'intents': ['Delivery & Shipping', 'Refunds & Returns'],
        'prompts': {'intent_classification': "Prompt {brand} {intents} {text}"}
    }
    classifier = AIIntentClassifier(mock_llm, config)
    
    # Case 1: Valid intent that should be mapped
    mock_llm.call.return_value = '{"intent": "Delivery & Shipping", "confidence": 0.9, "reason": "test", "alternative_intents": []}'
    res = classifier.classify("test")
    print(f"Delivery & Shipping -> {res['intent']} (Expected: Order & Logistics)")
    
    # Case 2: Intent that should NOT be mapped
    mock_llm.call.return_value = '{"intent": "Account Access", "confidence": 0.9, "reason": "test", "alternative_intents": []}'
    res = classifier.classify("test")
    print(f"Account Access -> {res['intent']} (Expected: Account Access)")

    # Case 3: Malformed JSON
    mock_llm.call.return_value = "Not JSON"
    res = classifier.classify("test")
    print(f"Malformed JSON -> {res['intent']} (Expected: General Inquiry)")

    # Case 4: Wrong confidence type
    mock_llm.call.return_value = '{"intent": "Delivery & Shipping", "confidence": "high", "reason": "test", "alternative_intents": []}'
    res = classifier.classify("test")
    print(f"Confidence 'high' -> {res['confidence']} (Expected: 0.9)")

if __name__ == "__main__":
    test_mapping()
