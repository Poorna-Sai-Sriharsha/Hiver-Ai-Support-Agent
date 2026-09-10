from unittest.mock import patch

import requests

from src.utils.llm_client import LLMClient


def test_ollama_failure():
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        client = LLMClient()
        client.provider = "ollama"
        client.mock_mode = False
        
        res = client.call("test prompt")
        print(f"Ollama failure response: {res}")
        if "Mock response" in res:
            print("RESULT: PASS - Fell back to mock.")
        else:
            print("RESULT: FAIL - Did not fall back to mock.")

if __name__ == "__main__":
    test_ollama_failure()
