import json
import logging
import os
import sys

import pandas as pd
import yaml
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from src.agent import SupportAgent
from src.intent.trivial_baseline import TrivialIntentClassifier
from src.retrieval.simple_baseline import SimpleIntentClassifier
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class EvaluationHarness:
    """
    Coordinates the evaluation of different system versions on a golden set.
    """
    def __init__(self, golden_set_path: str, train_data_path: str, config_path: str):
        self.golden_set = pd.read_csv(golden_set_path)
        self.train_df = pd.read_csv(train_data_path)
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.llm = LLMClient()

    def evaluate_intent(self, classifier):
        """
        Calculates intent metrics.
        """
        y_true = self.golden_set['gold_intent']
        y_pred = []
        for i, text in enumerate(self.golden_set['customer_message']):
            if i % 10 == 0:
                logger.info(f"Classifying intent: {i}/{len(self.golden_set)}")
            if hasattr(classifier, 'predict'):
                res = classifier.predict(text)
                intent = res['intent'] if isinstance(res, dict) else res
            else:
                res = classifier.classify(text)
                intent = res['intent']
            y_pred.append(intent)

        acc = accuracy_score(y_true, y_pred)
        precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, average='macro')

        support_list = support.tolist() if support is not None else []
        cm = confusion_matrix(y_true, y_pred).tolist()

        return {
            "accuracy": float(acc),
            "macro_f1": float(f1),
            "precision": float(precision),
            "recall": float(recall),
            "confusion_matrix": cm,
            "support": support_list
        }

    def evaluate_escalation(self, agent):
        """
        Calculates escalation metrics.
        """
        y_true = self.golden_set['should_escalate']
        y_pred = []
        for i, (_, row) in enumerate(self.golden_set.iterrows()):
            if i % 10 == 0:
                logger.info(f"Evaluating escalation: {i}/{len(self.golden_set)}")
            res = agent.process_message(row['customer_message'])
            y_pred.append("Yes" if res['escalation']['decision'] == "ESCALATED" else "No")

        acc = accuracy_score(y_true, y_pred)
        false_auto_handle = sum((t == "Yes" and p == "No") for t, p in zip(y_true, y_pred))

        return {
            "accuracy": float(acc),
            "false_auto_handle_rate": float(false_auto_handle / len(y_true))
        }

    def run_full_pipeline(self, output_file="artifacts/metrics.json"):
        """
        Runs all baselines and the AI agent, then saves results.
        """
        logger.info(f"Starting full evaluation pipeline. Output: {output_file}")

        # 1. Trivial Baseline
        trivial_intent = TrivialIntentClassifier(self.train_df)
        trivial_metrics = self.evaluate_intent(trivial_intent)

        # 2. Simple Baseline
        simple_intent = SimpleIntentClassifier(self.train_df)
        simple_metrics = self.evaluate_intent(simple_intent)

        # 3. AI Agent
        kb = VectorStore()
        kb.index_data(self.train_df)
        agent = SupportAgent("config/config.yaml", kb, self.llm)

        # Capture raw predictions for aggregation
        y_true_intent = self.golden_set['gold_intent'].tolist()
        y_pred_ai_intent = []
        for text in self.golden_set['customer_message']:
            res = agent.classifier.classify(text)
            y_pred_ai_intent.append(res['intent'])

        y_true_esc = self.golden_set['should_escalate'].tolist()
        y_pred_ai_esc = []
        for _, row in self.golden_set.iterrows():
            res = agent.process_message(row['customer_message'])
            y_pred_ai_esc.append("Yes" if res['escalation']['decision'] == "ESCALATED" else "No")

        # Calculate metrics using the captured predictions
        def get_intent_metrics(true, pred):
            acc = accuracy_score(true, pred)
            precision, recall, f1, support = precision_recall_fscore_support(true, pred, average='macro')
            return {
                "accuracy": float(acc),
                "macro_f1": float(f1),
                "precision": float(precision),
                "recall": float(recall),
                "confusion_matrix": confusion_matrix(true, pred).tolist(),
                "support": support.tolist() if support is not None else []
            }

        ai_intent_metrics = get_intent_metrics(y_true_intent, y_pred_ai_intent)

        acc_esc = accuracy_score(y_true_esc, y_pred_ai_esc)
        false_auto = sum((t == "Yes" and p == "No") for t, p in zip(y_true_esc, y_pred_ai_esc))
        ai_esc_metrics = {
            "accuracy": float(acc_esc),
            "false_auto_handle_rate": float(false_auto / len(y_true_esc))
        }

        results = {
            "trivial": trivial_metrics,
            "simple": simple_metrics,
            "ai": {
                "intent": ai_intent_metrics,
                "escalation": ai_esc_metrics
            },
            "raw": {
                "y_true_intent": y_true_intent,
                "y_pred_ai_intent": y_pred_ai_intent,
                "y_true_esc": y_true_esc,
                "y_pred_ai_esc": y_pred_ai_esc
            }
        }

        # Save to artifacts
        os.makedirs("artifacts", exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)

        logger.info(f"Evaluation complete. Results saved to {output_file}")

if __name__ == "__main__":
    # Default to full set if no indices provided
    start_idx = 0
    end_idx = None

    if len(sys.argv) > 1:
        try:
            start_idx = int(sys.argv[1])
        except ValueError:
            logger.error("Invalid start index provided.")
    if len(sys.argv) > 2:
        try:
            end_idx = int(sys.argv[2])
        except ValueError:
            logger.error("Invalid end index provided.")

    harness = EvaluationHarness(
        golden_set_path="evaluation/golden_set.csv",
        train_data_path="data/processed/train.csv",
        config_path="config/config.yaml"
    )

    # Slice the golden set for batch evaluation
    harness.golden_set = harness.golden_set.iloc[start_idx:end_idx]

    # Generate output filename based on slice
    output_filename = f"artifacts/metrics_{start_idx}_{end_idx if end_idx else 'end'}.json"
    harness.run_full_pipeline(output_file=output_filename)
