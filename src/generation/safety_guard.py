import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafetyGuard:
    """
    Final safety and grounding check for generated responses.
    """
    def __init__(self):
        # PII patterns
        self.pii_patterns = {
            "email": r'[\w\.-]+@[\w\.-]+\.\w+',
            "phone": r'\b\d{10,}\b',
            "credit_card": r'\b(?:\d[ -]*?){13,16}\b',
            "order_id": r'ORDER\s*#?\s*\d{5,}',
        }

    def check_input(self, text: str) -> tuple[bool, str | None]:
        """
        Checks the customer's input for PII or malicious content before processing.
        """
        for label, pattern in self.pii_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return False, f"PII detected in input: {label}"

        injection_keywords = ["ignore all previous", "system prompt", "you are now a", "act as a"]
        if any(kw in text.lower() for kw in injection_keywords):
            return False, "Potential prompt injection detected"

        return True, None

    def check(self, reply: str, evidence: str) -> tuple[bool, str | None]:
        """
        Checks for PII leakage, hallucinations, or inappropriate language.
        Returns (is_safe, error_message).
        """
        # 1. PII Leakage Check
        for label, pattern in self.pii_patterns.items():
            if re.search(pattern, reply, re.IGNORECASE):
                return False, f"PII Leakage detected: {label}"

        # 2. Grounding Check
        numbers_in_reply = re.findall(r'\d+', reply)
        for num in numbers_in_reply:
            if num not in evidence:
                if len(num) > 3:
                    return False, f"Potential hallucination: number {num} not found in evidence"

        # 3. Inappropriate Language
        bad_words = ["stupid", "idiot", "hate", "worst"]
        if any(word in reply.lower() for word in bad_words):
            return False, "Inappropriate language detected"

        return True, None
