import json
import logging
from typing import Any

from .agent import SupportAgent
from .llm_judge import LLMJudge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Evaluator:
    """
    Evaluation harness for the AI Support Agent.
    """
    def __init__(self, agent: SupportAgent):
        self.agent = agent
        self.judge = LLMJudge(agent.llm)

    def evaluate_golden_set(self, golden_set_path: str) -> dict[str, Any]:
        """
        Runs the agent against a hand-labelled golden set and computes metrics.
        """
        with open(golden_set_path, 'r') as f:
            golden_set = json.load(f)

        results = []
        correct_intents = 0
        correct_escalations = 0

        for example in golden_set:
            query = example['query']
            ground_truth = example['ground_truth']

            prediction = self.agent.process_message(query)

            # Intent Accuracy
            if prediction['intent'] == ground_truth['intent']:
                correct_intents += 1

            # Escalation Accuracy
            pred_dec = prediction['escalation']['decision']
            gt_dec = ground_truth['escalation']
            if pred_dec == gt_dec:
                correct_escalations += 1
            else:
                logger.info(f"Escalation Mismatch: Query='{query[:30]}...', Pred={pred_dec}, GT={gt_dec}")

            results.append({
                "query": query,
                "ground_truth": ground_truth,
                "prediction": prediction
            })

        accuracy_intent = correct_intents / len(golden_set)
        accuracy_escalation = correct_escalations / len(golden_set)

        return {
            "total_examples": len(golden_set),
            "intent_accuracy": accuracy_intent,
            "escalation_accuracy": accuracy_escalation,
            "detailed_results": results
        }

    def llm_judge_review(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Uses an LLM to judge the quality of the replies based on a rubric.
        """
        judgments = []
        for res in results:
            prediction = res['prediction']
            # The agent result should have 'reply', 'evidence', etc.
            # We assume results are from process_message output
            score = self.judge.judge(
                customer_message=res['query'],
                context="", # Simplified
                reply=prediction['reply'],
                evidence=prediction.get('evidence', []),
                expected_points=res['ground_truth'].get('expected_response_points', "N/A")
            )
            judgments.append({
                "query": res['query'],
                "scores": score,
                "reasoning": score['reasoning']
            })
        return judgments
