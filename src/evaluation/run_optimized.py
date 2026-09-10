import gc
import json
import logging
import os

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

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message) s')
logger = logging.getLogger(__name__)

class EvaluationHarness:
    def __init__(self, golden_set_path: str, train_data_path: str, config_path: str):
        self.golden_set = pd.read_csv(golden_set_path)
        self.train_df = pd.read_csv(train_data_path)
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.llm = LLMClient()

    def run_optimized_pipeline(self, batch_size=10):
        logger.info(f"Starting optimized evaluation pipeline. Batch size: {batch_size}")
        
        # Index ONCE
        kb = VectorStore()
        kb.index_data(self.train_df)
        agent = SupportAgent("config/config.yaml", kb, self.llm)
        
        # Baselines
        trivial_intent = TrivialIntentClassifier(self.train_df)
        simple_intent = SimpleIntentClassifier(self.train_df)
        
        y_true_intent = self.golden_set['gold_intent'].tolist()
        y_true_esc = self.golden_set['should_escalate'].tolist()
        
        y_pred_trivial = []
        y_pred_simple = []
        y_pred_ai_intent = []
        y_pred_ai_esc = []
        
        # Process in chunks to manage memory
        for i in range(0, len(self.golden_set), batch_size):
            end = min(i + batch_size, len(self.golden_set))
            logger.info(f"Processing slice {i} to {end}...")
            
            chunk = self.golden_set.iloc[i:end]
            
            for _, row in chunk.iterrows():
                text = row['customer_message']
                
                # Trivial
                res_t = trivial_intent.predict(text)
                y_pred_trivial.append(res_t['intent'] if isinstance(res_t, dict) else res_t)
                
                # Simple
                res_s = simple_intent.predict(text)
                y_pred_simple.append(res_s['intent'] if isinstance(res_s, dict) else res_s)
                
                # AI
                res_ai = agent.process_message(text)
                y_pred_ai_intent.append(res_ai['intent'])
                y_pred_ai_esc.append("Yes" if res_ai['escalation']['decision'] == "ESCALATED" else "No")
            
            gc.collect() # Clear memory after each batch
            
        # Calculate final metrics
        def get_metrics(true, pred):
            acc = accuracy_score(true, pred)
            precision, recall, f1, support = precision_recall_fscore_support(true, pred, average='macro', zero_division=0)
            return {
                "accuracy": float(acc),
                "macro_f1": float(f1),
                "precision": float(precision),
                "recall": float(recall),
                "confusion_matrix": confusion_matrix(true, pred).tolist(),
                "support": support.tolist() if support is not None else []
            }

        results = {
            "trivial": get_metrics(y_true_intent, y_pred_trivial),
            "simple": get_metrics(y_true_intent, y_pred_simple),
            "ai": {
                "intent": get_metrics(y_true_intent, y_pred_ai_intent),
                "escalation": {
                    "accuracy": float(accuracy_score(y_true_esc, y_pred_ai_esc)),
                    "false_auto_handle_rate": float(sum((t == "Yes" and p == "No") for t, p in zip(y_true_esc, y_pred_ai_esc)) / len(y_true_esc))
                }
            },
            "raw": {
                "y_true_intent": y_true_intent,
                "y_pred_ai_intent": y_pred_ai_intent,
                "y_true_esc": y_true_esc,
                "y_pred_ai_esc": y_pred_ai_esc
            }
        }
        
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/metrics.json", "w") as f:
            json.dump(results, f, indent=4)
        
        logger.info("Full optimized evaluation complete. Results saved to artifacts/metrics.json")

if __name__ == "__main__":
    harness = EvaluationHarness(
        golden_set_path="evaluation/golden_set.csv",
        train_data_path="data/processed/train.csv",
        config_path="config/config.yaml"
    )
    harness.run_optimized_pipeline(batch_size=10)
