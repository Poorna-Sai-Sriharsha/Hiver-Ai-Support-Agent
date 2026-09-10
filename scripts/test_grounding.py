from unittest.mock import MagicMock

from src.generation.ai_generator import AIResponseGenerator


def test_grounding():
    mock_llm = MagicMock()
    config = {
        'brand': {'name': 'AmazonHelp'},
        'prompts': {'reply_generation': "Prompt {brand} {context} {text}"}
    }
    gen = AIResponseGenerator(mock_llm, config)
    
    evidence = [
        {'customer_message': 'Order late', 'brand_response': 'We are sorry for the delay.'}
    ]
    
    # Case 1: Grounded response (shares keywords)
    mock_llm.call.return_value = "We are sorry for the delay."
    res = gen.generate("Where is my order?", "", evidence)
    print(f"Grounded reply score: {res['grounding_score']}")
    
    # Case 2: Ungrounded response (no overlap)
    mock_llm.call.return_value = "I am a robot and I like cheese."
    res = gen.generate("Where is my order?", "", evidence)
    print(f"Ungrounded reply score: {res['grounding_score']}")

if __name__ == "__main__":
    test_grounding()
