from unittest.mock import patch

from src.utils.llm_client import LLMClient, retry_with_backoff


def test_mock_mode_activation():
    # Test that missing API key triggers mock mode
    with patch.dict('os.environ', {'LLM_API_KEY': ''}):
        client = LLMClient()
        assert client.mock_mode is True

def test_mock_call_responses():
    client = LLMClient()
    client.mock_mode = True

    # Test intent mock
    res = client.call("Please classify this message")
    assert "intent" in res

    # Test decision mock
    res = client.call("Make a decision on this")
    assert "decision" in res

def test_retry_logic():
    # Test the retry decorator logic independently to ensure it works
    call_count = 0
    @retry_with_backoff(retries=2, backoff_in_seconds=0)
    def fail_twice_then_succeed():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary Fail")
        return "Success"

    with patch('time.sleep', return_value=None):
        res = fail_twice_then_succeed()
        assert res == "Success"
        assert call_count == 3
