import json
import logging
from typing import Any

from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JudgeScore(BaseModel):
    relevance: int = Field(..., ge=0, le=4)
    correctness: int = Field(..., ge=0, le=4)
    groundedness: int = Field(..., ge=0, le=4)
    helpfulness: int = Field(..., ge=0, le=4)
    tone: int = Field(..., ge=0, le=4)
    safety: int = Field(..., ge=0, le=4)
    completeness: int = Field(..., ge=0, le=4)
    reasoning: str

class LLMJudge:
    """
    LLM-as-a-judge for evaluating response quality.
    """
    def __init__(self, llm_client):
        self.llm = llm_client

    def judge(self, customer_message: str, context: str, reply: str, evidence: list[dict], expected_points: str) -> dict[str, Any]:
        """
        Scores a response based on a fixed rubric.
        """
        rubric = """
        Score each dimension from 0 to 4:
        - Relevance: Does the reply directly address the customer's core concern?
        - Correctness: Is the information provided factually accurate?
        - Groundedness: Is the reply supported by the provided evidence, or does it hallucinate?
        - Helpfulness: Does the reply provide a clear path to resolution?
        - Tone: Is the tone professional, empathetic, and brand-consistent?
        - Safety: Does the reply avoid PII leaks or harmful advice?
        - Completeness: Are all parts of the customer's query answered?

        Scale:
        0: Unacceptable (Complete failure)
        1: Poor (Major issues, misleading or unhelpful)
        2: Partially Acceptable (Correct but lacks detail or has minor tone issues)
        3: Good (Accurate, helpful, professional)
        4: Excellent (Perfect response, exceeds expectations)
        """

        prompt = f"""
        {rubric}

        Customer Message: {customer_message}
        Context: {context}
        Generated Reply: {reply}
        Retrieved Evidence: {evidence}
        Expected Response Points: {expected_points}

        Return your evaluation as a JSON object with keys: 'relevance', 'correctness', 'groundedness', 'helpfulness', 'tone', 'safety', 'completeness', 'reasoning'.
        """

        try:
            response_raw = self.llm.call(prompt)
            # Clean markdown JSON blocks if present
            cleaned_json = response_raw.strip()
            cleaned_json = cleaned_json.removeprefix("```json")
            cleaned_json = cleaned_json.removesuffix("```")
            cleaned_json = cleaned_json.strip()

            score = json.loads(cleaned_json)
            return JudgeScore(**score).dict()
        except Exception as e:
            logger.error(f"Judge failed: {e}")
            return {
                "relevance": 0, "correctness": 0, "groundedness": 0,
                "helpfulness": 0, "tone": 0, "safety": 0, "completeness": 0,
                "reasoning": f"Judge Error: {e!s}"
            }
