import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EscalationSystem:
    """
    Hybrid escalation system combining measurable signals and LLM reasoning.
    """
    def __init__(self, llm_client, config):
        self.llm = llm_client
        self.config = config

    def decide(self, text: str, reply: str, retrieval_score: float, intent: str) -> dict[str, Any]:
        """
        Decides whether to AUTO-HANDLE or ESCALATE.
        """
        signals = []
        decision = "AUTO_HANDLED"

        # 1. Measurable Signals
        # Signal: Low retrieval similarity
        if retrieval_score < 0.3:
            signals.append("LOW_RETRIEVAL_CONFIDENCE")
            decision = "ESCALATED"

        # Signal: Safety-sensitive intents
        if intent in ["Severe Complaint / Fraud", "Account & Security"]:
            signals.append("SENSITIVE_INTENT")
            decision = "ESCALATED"

        # Signal: Extreme sentiment (simulated by keyword check)
        if any(word in text.lower() for word in ["legal", "court", "sue", "lawyer", "fraud"]):
            signals.append("LEGAL_OR_FRAUD_TRIGGER")
            decision = "ESCALATED"

        # 2. LLM Reasoning (for nuanced cases)
        escalation_prompt = self.config['prompts']['escalation_reasoning'].format(
            brand=self.config['brand']['name'],
            text=text,
            reply=reply
        )
        # Add structured output requirement
        escalation_prompt += "\n\nReturn JSON with keys: 'decision', 'reason'."

        try:
            llm_raw = self.llm.call(escalation_prompt)
            import json
            llm_res = json.loads(llm_raw)
            llm_decision = llm_res.get("decision", "AUTO_HANDLED")
            llm_reason = llm_res.get("reason", "No reason provided.")

            if llm_decision == "ESCALATED":
                signals.append("LLM_ESCALATION_TRIGGER")
                decision = "ESCALATED"
        except Exception as e:
            logger.error(f"Escalation LLM call failed: {e}")
            llm_reason = "LLM failure during reasoning."

        # Construct the reason based on signals
        if decision == "ESCALATED":
            reason_parts = []
            if "LOW_RETRIEVAL_CONFIDENCE" in signals:
                reason_parts.append("low historical evidence")
            if "SENSITIVE_INTENT" in signals:
                reason_parts.append("sensitive intent category")
            if "LEGAL_OR_FRAUD_TRIGGER" in signals:
                reason_parts.append("legal or fraud keywords detected")
            if "LLM_ESCALATION_TRIGGER" in signals:
                reason_parts.append(f"LLM reasoning: {llm_reason}")

            final_reason = "; ".join(reason_parts) if reason_parts else llm_reason
        else:
            final_reason = "Standard automation criteria met."

        return {
            "decision": decision,
            "reason": final_reason,
            "signals": signals,
            "confidence": 1.0 if signals else 0.5
        }
