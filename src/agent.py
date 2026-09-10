import logging
from typing import Any

from src.escalation.escalation_system import EscalationSystem
from src.generation.ai_generator import AIResponseGenerator
from src.generation.safety_guard import SafetyGuard
from src.intent.ai_classifier import AIIntentClassifier
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupportAgent:
    """
    The full AI Support Agent orchestrating the modular pipeline.
    """
    def __init__(self, config_path: str, kb: VectorStore, llm_client: LLMClient = None):
        import yaml
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.kb = kb
        self.llm = llm_client or LLMClient()

        # Initialize modules
        self.classifier = AIIntentClassifier(self.llm, self.config)
        self.generator = AIResponseGenerator(self.llm, self.config)
        self.escalator = EscalationSystem(self.llm, self.config)
        self.guard = SafetyGuard()

    def process_message(self, text: str, context: str = "") -> dict[str, Any]:
        """
        Full pipeline: Input Safety -> Intent -> Retrieval -> Generation -> Output Safety -> Escalation.
        """
        logger.info(f"Processing message: {text[:50]}...")

        # 0. Input Safety Check
        is_input_safe, input_error = self.guard.check_input(text)
        if not is_input_safe:
            logger.warning(f"Input safety check failed: {input_error}")
            return {
                "original_message": text,
                "intent": "SAFETY_VIOLATION",
                "intent_confidence": 1.0,
                "reply": "I'm sorry, but I cannot process this request due to a safety violation. Please contact support via official channels.",
                "escalation": {"decision": "ESCALATED", "reason": f"Input Safety Violation: {input_error}", "signals": ["INPUT_SAFETY_VIOLATION"]},
                "evidence": [],
                "grounding_score": 0.0,
                "grounding_details": []
            }

        # 1. Intent Classification
        intent_res = self.classifier.classify(text)
        intent = intent_res['intent']

        # 2. Grounded Retrieval
        evidence = self.kb.retrieve(text, k=3)
        retrieval_score = evidence[0]['score'] if evidence else 0.0

        # 3. Response Generation
        gen_res = self.generator.generate(text, context, evidence)
        reply = gen_res['reply']

        # 4. Output Safety Guard
        is_safe, safety_error = self.guard.check(reply, str(evidence))
        if not is_safe:
            logger.warning(f"Output safety check failed: {safety_error}")
            reply = "I'm sorry, I cannot provide a response to this request at the moment. Please wait while I connect you to a human agent."
            decision_override = "ESCALATED"
            reason_override = f"Output Safety Violation: {safety_error}"
        else:
            decision_override = None
            reason_override = None

        # 5. Escalation Decision
        esc_res = self.escalator.decide(text, reply, retrieval_score, intent)

        if decision_override:
            esc_res['decision'] = decision_override
            esc_res['reason'] = reason_override

        return {
            "original_message": text,
            "intent": intent,
            "intent_confidence": intent_res['confidence'],
            "reply": reply,
            "escalation": esc_res,
            "evidence": evidence,
            "grounding_score": gen_res['grounding_score'],
            "grounding_details": gen_res.get('grounding_details', [])
        }
