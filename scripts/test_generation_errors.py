from unittest.mock import MagicMock

from src.generation.ai_generator import AIResponseGenerator


def test_errors():
    mock_llm = MagicMock()
    config = {
        'brand': {'name': 'AmazonHelp'},
        'prompts': {'reply_generation': "Prompt"}
    }
    gen = AIResponseGenerator(mock_llm, config)
    
    # Case 1: LLM raises exception
    mock_llm.call.side_effect = Exception("API Down")
    res = gen.generate("test", "", [])
    print(f"Error response: {res['reply']}")
    
if __name__ == "__main__":
    test_errors()
