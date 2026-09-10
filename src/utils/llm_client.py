import logging
import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import logging
import time

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    """Decorator for exponential backoff retries on API calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logger.error(f"Max retries reached for {func.__name__}. Final error: {e}")
                        raise e
                    sleep = (backoff_in_seconds * 2 ** x)
                    logger.warning(f"API call failed: {e}. Retrying in {sleep}s... ({x+1}/{retries})")
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator

class LLMClient:
    """
    Unified client for interacting with different LLM providers.
    Supports: 'anthropic', 'openai', 'ollama'.
    """
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
        self.api_key = os.getenv("LLM_API_KEY")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

        if self.provider == "ollama":
            try:
                requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                self.mock_mode = False
            except Exception:
                logger.warning(f"Ollama service not reachable at {self.ollama_url}. Falling back to MOCK mode.")
                self.mock_mode = True
        elif not self.api_key:
            logger.warning("LLM_API_KEY not found in environment. System will run in MOCK mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False

    def call(self, prompt: str, system_prompt: str = "") -> str:
        """
        Calls the selected LLM provider with integrated error handling and retries.
        """
        if self.mock_mode:
            return self._mock_call(prompt)

        try:
            if self.provider == "anthropic":
                return self._call_anthropic(prompt, system_prompt)
            elif self.provider == "openai":
                return self._call_openai(prompt, system_prompt)
            elif self.provider == "ollama":
                return self._call_ollama(prompt, system_prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"Critical LLM failure: {e}")
            # Safe fallback: do not fabricate a response, but return a marker that the system can use to escalate
            return '{"error": "LLM_UNAVAILABLE", "decision": "ESCALATED", "reason": "LLM service unavailable"}'

    @retry_with_backoff()
    def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    @retry_with_backoff()
    def _call_openai(self, prompt: str, system_prompt: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    @retry_with_backoff()
    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """
        Calls the local Ollama API.
        """
        response = requests.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=300
        )
        response.raise_for_status()
        return response.json()['message']['content']

    def _mock_call(self, prompt: str) -> str:
        """
        Deterministic mock responses for development and testing.
        """
        p = prompt.lower()
        if "classify" in p:
            return '{"intent": "Delivery & Shipping", "confidence": 0.9, "reason": "Mocked", "alternative_intents": []}'
        if "decision" in p:
            return '{"decision": "AUTO_HANDLED", "reason": "Mocked"}'
        if "reply" in p or "response" in p:
            return "Thank you for contacting support. We are looking into your issue."
        return "Mock response"

    def _mock_call(self, prompt: str) -> str:
        """
        Deterministic mock responses for development and testing.
        """
        p = prompt.lower()
        if "classify" in p:
            return '{"intent": "Delivery & Shipping", "confidence": 0.9, "reason": "Mocked", "alternative_intents": []}'
        if "decision" in p:
            return '{"decision": "AUTO_HANDLED", "reason": "Mocked"}'
        if "reply" in p or "response" in p:
            return "Thank you for contacting support. We are looking into your issue."
        return "Mock response"
