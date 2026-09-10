import json
import os

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)

from src.intent.trivial_baseline import TrivialIntentClassifier
from src.retrieval.simple_baseline import SimpleIntentClassifier


def aggregate_metrics():
    artifacts_dir = 'artifacts'
    batch_files = [f for f in os.listdir(artifacts_dir) if f.startswith('metrics_') and f.endswith('.json')]

    if not batch_files:
        print("No batch files found.")
        return

    # Sort files to ensure order matches the dataset
    # Filenames are metrics_0_20.json, metrics_20_40.json, etc.
    # We should sort by the start index.
    def get_start_idx(filename):
        try:
            return int(filename.split('_')[1])
        except (IndexError, ValueError):
            return 0

    batch_files.sort(key=get_start_idx)
    print(f"Found {len(batch_files)} batch files: {batch_files}")

    all_y_true_intent = []
    all_y_pred_intent = []
    all_y_true_esc = []
    all_y_pred_esc = []

    for file in batch_files:
        with open(os.path.join(artifacts_dir, file), 'r') as f:
            data = json.load(f)
            if 'raw' in data:
                all_y_true_intent.extend(data['raw']['y_true_intent'])
                all_y_pred_intent.extend(data['raw']['y_pred_ai_intent'])
                all_y_true_esc.extend(data['raw']['y_true_esc'])
                all_y_pred_esc.extend(data['raw']['y_pred_ai_esc'])
            else:
                print(f"Warning: No raw data in {file}")

    if not all_y_true_intent:
        print("No raw data collected.")
        return

    # 1. Calculate AI Intent Metrics
    acc_intent = accuracy_score(all_y_true_intent, all_y_pred_intent)
    precision, recall, f1, support = precision_recall_fscore_support(all_y_true_intent, all_y_pred_intent, average='macro')
    cm_intent = confusion_matrix(all_y_true_intent, all_y_pred_intent).tolist()

    ai_intent_metrics = {
        "accuracy": float(acc_intent),
        "macro_f1": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "confusion_matrix": cm_intent,
        "support": support.tolist() if support is not None else []
    }

    # 2. Calculate AI Escalation Metrics
    acc_esc = accuracy_score(all_y_true_esc, all_y_pred_esc)
    false_auto = sum((t == "Yes" and p == "No") for t, p in zip(all_y_true_esc, all_y_pred_esc))
    ai_esc_metrics = {
        "accuracy": float(acc_esc),
        "false_auto_handle_rate": float(false_auto / len(all_y_true_esc))
    }

    # 3. Calculate Baselines on the full set
    golden_set = pd.read_csv('evaluation/golden_set.csv')
    train_df = pd.read_csv('data/processed/train.csv')
    y_true_intent = golden_set['gold_intent'].tolist()

    # Trivial Baseline
    trivial = TrivialIntentClassifier(train_df)
    y_pred_trivial = [trivial.predict(text) for text in golden_set['customer_message']]
    # trivial.predict might return a dict or string depending on implementation
    y_pred_trivial = [res['intent'] if isinstance(res, dict) else res for res in y_pred_trivial]

    t_acc = accuracy_score(y_true_intent, y_pred_trivial)
    t_prec, t_rec, t_f1, t_supp = precision_recall_fscore_support(y_true_intent, y_pred_trivial, average='macro')
    trivial_metrics = {
        "accuracy": float(t_acc),
        "macro_f1": float(t_f1),
        "precision": float(t_prec),
        "recall": float(t_rec),
        "confusion_matrix": confusion_matrix(y_true_intent, y_pred_trivial).tolist(),
        "support": t_supp.tolist() if t_supp is not None else []
    }

    # Simple Baseline
    simple = SimpleIntentClassifier(train_df)
    y_pred_simple = [simple.predict(text) for text in golden_set['customer_message']]
    y_pred_simple = [res['intent'] if isinstance(res, dict) else res for res in y_pred_simple]

    s_acc = accuracy_score(y_true_intent, y_pred_simple)
    s_prec, s_rec, s_f1, s_supp = precision_recall_fscore_support(y_true_intent, y_pred_simple, average='macro')
    simple_metrics = {
        "accuracy": float(s_acc),
        "macro_f1": float(s_f1),
        "precision": float(s_prec),
        "recall": float(s_rec),
        "confusion_matrix": confusion_matrix(y_true_intent, y_pred_simple).tolist(),
        "support": s_supp.tolist() if s_supp is not None else []
    }

    results = {
        "trivial": trivial_metrics,
        "simple": simple_metrics,
        "ai": {
            "intent": ai_intent_metrics,
            "escalation": ai_esc_metrics
        },
        "raw": {
            "y_true_intent": all_y_true_intent,
            "y_pred_ai_intent": all_y_pred_intent,
            "y_true_esc": all_y_true_esc,
            "y_pred_ai_esc": all_y_pred_esc
        }
    }

    with open('artifacts/metrics.json', 'w') as f:
        json.dump(results, f, indent=4)

    print("Aggregate metrics saved to artifacts/metrics.json")

if __name__ == "__main__":
    aggregate_metrics()
