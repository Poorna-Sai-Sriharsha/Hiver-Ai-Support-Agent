import logging
from typing import Any

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseMetadata(BaseModel):
    draft_reply: str
    evidence_ids: list[str]
    grounding_score: float
    generation_metadata: dict[str, Any]

class AIResponseGenerator:
    """
    Generates grounded support responses using retrieved evidence.
    """
    def __init__(self, llm_client, config):
        self.llm = llm_client
        self.config = config

    def generate(self, text: str, context: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Generates a grounded reply based on historical evidence.
        """
        # Format evidence
        evidence_text = ""
        evidence_ids = []
        for i, item in enumerate(evidence):
            evidence_text += f"Example {i+1}:\nCustomer: {item['customer_message']}\nResolution: {item['brand_response']}\n\n"
            # Use actual ID if available, otherwise index
            evidence_ids.append(str(item.get('id', i)))

        reply_prompt = self.config['prompts']['reply_generation'].format(
            brand=self.config['brand']['name'],
            context=evidence_text if evidence_text else "No relevant historical resolutions found.",
            text=text
        )

        try:
            reply = self.llm.call(reply_prompt).strip()

            # Advanced grounding check: Claim-Support Verification
            grounding_res = self._verify_grounding(reply, evidence_text)
            grounding_score = grounding_res['score']

            return {
                "reply": reply,
                "evidence": evidence,
                "grounding_score": grounding_score,
                "grounding_details": grounding_res['details'],
                "evidence_ids": evidence_ids
            }
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "reply": "I'm sorry, I'm having trouble processing your request. Please hold on while I connect you to a specialist.",
                "evidence": [],
                "grounding_score": 0.0,
                "grounding_details": [],
                "evidence_ids": []
            }

    def _verify_grounding(self, reply: str, evidence: str) -> dict[str, Any]:
        """
        Verifies grounding by extracting claims and checking them against evidence.
        """
        if not evidence:
            return {"score": 0.0, "details": []}

        # 1. Extract factual claims from the reply
        claims_prompt = f"""
        Extract all factual claims from the following customer support reply.
        A claim is any statement of fact, policy, or action.

        Reply: {reply}

        Return as a JSON list of strings. Example: ["The delivery is late", "Refunds take 5 days"].
        """
        try:
            claims_raw = self.llm.call(claims_prompt)
            import json
            # Clean markdown JSON blocks
            cleaned_json = claims_raw.strip()
            cleaned_json = cleaned_json.removeprefix("```json")
            cleaned_json = cleaned_json.removesuffix("```")
            cleaned_json = cleaned_json.strip()

            claims = json.loads(cleaned_json)
            if not isinstance(claims, list):
                claims = [claims] if claims else []
        except (json.JSONDecodeError, RuntimeError, ValueError):
            claims = []

        if not claims:
            return {"score": 1.0, "details": [], "note": "No factual claims found."}

        # 2. Verify each claim against evidence
        verified_claims = []
        supported_count = 0

        for claim in claims:
            verify_prompt = f"""
            Check if the following claim is supported by the provided evidence.

            Evidence: {evidence}
            Claim: {claim}

            Return JSON with keys: 'status' (SUPPORTED, PARTIALLY_SUPPORTED, UNSUPPORTED, CONTRADICTED) and 'reason'.
            """
            try:
                res_raw = self.llm.call(verify_prompt)
                # Clean markdown JSON blocks
                cleaned_json = res_raw.strip()
                cleaned_json = cleaned_json.removeprefix("```json")
                cleaned_json = cleaned_json.removesuffix("```")
                cleaned_json = cleaned_json.strip()

                res = json.loads(cleaned_json)
                status = res.get('status', 'UNSUPPORTED')
                if status == 'SUPPORTED':
                    supported_count += 1
                verified_claims.append({"claim": claim, "status": status, "reason": res.get('reason', "")})
            except (json.JSONDecodeError, RuntimeError, ValueError):
                verified_claims.append({"claim": claim, "status": "UNKNOWN", "reason": "Verification failed"})

        score = supported_count / len(claims)
        return {
            "score": score,
            "details": verified_claims
        }
