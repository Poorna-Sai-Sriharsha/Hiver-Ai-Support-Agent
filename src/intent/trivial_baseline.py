from typing import Any

import pandas as pd


class TrivialIntentClassifier:
    """
    A trivial baseline intent classifier that always predicts the majority class.
    """
    def __init__(self, train_data):
        if isinstance(train_data, str):
            df = pd.read_csv(train_data)
        elif isinstance(train_data, pd.DataFrame):
            df = train_data
        else:
            # Fallback for None or other types
            df = pd.DataFrame({'customer_message': []})

        # For trivial baseline, we need to determine the majority class from the dataset.
        # If df is empty or has no labels, we use a generic a-priori most common intent.
        self.majority_class = "Delivery & Shipping"
        if not df.empty and 'gold_intent' in df.columns:
             self.majority_class = df['gold_intent'].mode()[0]

    def predict(self, text: str) -> dict[str, Any]:
        return {
            "intent": self.majority_class,
            "confidence": 1.0,
            "reason": "Trivial baseline: always predicts majority class."
        }

class TrivialResponseGenerator:
    """
    A trivial baseline response generator that always returns a generic fallback.
    """
    def generate(self, text: str, context: str, retrieved_evidence: list) -> str:
        return "Thank you for contacting our support. We have received your message and a representative will get back to you soon."

class TrivialEscalationReasoner:
    """
    A trivial baseline escalation reasoner that always escalates.
    """
    def decide(self, text: str, reply: str) -> dict[str, Any]:
        return {
            "decision": "ESCALATED",
            "reason": "Trivial baseline: always escalates for safety."
        }
