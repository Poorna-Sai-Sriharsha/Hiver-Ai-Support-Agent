import json
import logging
from typing import Any

from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentPrediction(BaseModel):
    intent: str = Field(..., description="The classified intent from the taxonomy")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0")
    reason: str = Field(..., description="Reasoning for this classification")
    alternative_intents: list[str] = Field(default=[], description="Other possible intents")

class AIIntentClassifier:
    """
    LLM-assisted intent classifier with structured output.
    """
    def __init__(self, llm_client, config):
        self.llm = llm_client
        self.config = config
        self.intents = config['intents']

    def classify(self, text: str) -> dict[str, Any]:
        """
        Classifies a message into one of the predefined intents.
        """
        logger.info(f"AI Classifying text: {text[:50]}...")
        prompt = self.config['prompts']['intent_classification'].format(
            brand=self.config['brand']['name'],
            intents=", ".join(self.intents),
            text=text
        )

        # Add structured output instruction
        prompt += "\n\nReturn your response as a JSON object with the following keys: 'intent', 'confidence', 'reason', 'alternative_intents'."

        try:
            logger.info("Calling LLM for classification...")
            response_raw = self.llm.call(prompt)
            logger.info(f"LLM response received: {response_raw[:100]}...")
            # Try to parse JSON
            prediction = json.loads(response_raw)

            # Ensure alternative_intents is a list of strings
            if "alternative_intents" in prediction:
                alt = prediction["alternative_intents"]
                if isinstance(alt, str):
                    prediction["alternative_intents"] = [i.strip() for i in alt.split(",") if i.strip()]
                elif isinstance(alt, list):
                    # Flatten if it's a list of lists
                    flattened = []
                    for item in alt:
                        if isinstance(item, list):
                            flattened.extend(item)
                        elif isinstance(item, str):
                            flattened.append(item)
                    prediction["alternative_intents"] = flattened
                else:
                    prediction["alternative_intents"] = []

            # Ensure confidence is a float
            if "confidence" in prediction:
                conf = prediction["confidence"]
                if isinstance(conf, str):
                    conf_lower = conf.lower()
                    if "high" in conf_lower:
                        prediction["confidence"] = 0.9
                    elif "medium" in conf_lower:
                        prediction["confidence"] = 0.5
                    elif "low" in conf_lower:
                        prediction["confidence"] = 0.2
                    else:
                        try:
                            prediction["confidence"] = float(conf)
                        except ValueError:
                            prediction["confidence"] = 0.0
                elif not isinstance(conf, (int, float)):
                    prediction["confidence"] = 0.0

            # Validate with Pydantic
            validated = IntentPrediction(**prediction)
            res = validated.dict()

            return res
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Classification failed or malformed: {e}")
            # Safe fallback
            return {
                "intent": "General Inquiry",
                "confidence": 0.0,
                "reason": f"Failed to parse LLM response: {e!s}",
                "alternative_intents": []
            }
