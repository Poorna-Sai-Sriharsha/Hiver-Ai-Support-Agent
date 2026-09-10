import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_comprehensive_audit():
    # Paths
    train_path = 'data/processed/train.csv'
    val_path = 'data/processed/val.csv'
    test_path = 'data/processed/test.csv'
    golden_path = 'evaluation/annotation_queue.csv'

    if not all(os.path.exists(p) for p in [train_path, val_path, test_path, golden_path]):
        logger.error("One or more data files missing. Audit aborted.")
        return

    # Load datasets
    train = pd.read_csv(train_path)
    val = pd.read_csv(val_path)
    test = pd.read_csv(test_path)
    golden = pd.read_csv(golden_path)
    
    # 1. Tweet ID / Conversation ID Overlap
    def get_ids(df):
        return set(df['conversation_id'].astype(str))

    train_ids = get_ids(train)
    val_ids = get_ids(val)
    test_ids = get_ids(test)
    golden_ids = get_ids(golden)

    overlaps = {
        "train-val": train_ids.intersection(val_ids),
        "train-test": train_ids.intersection(test_ids),
        "val-test": val_ids.intersection(test_ids),
        "train-golden": train_ids.intersection(golden_ids),
        "val-golden": val_ids.intersection(golden_ids),
        "test-golden": test_ids.intersection(golden_ids),
    }

    # 2. Text-based Duplicates (Exact and Normalized)
    def get_texts(df):
        return set(df['customer_message'].astype(str))

    train_texts = get_texts(train)
    val_texts = get_texts(val)
    test_texts = get_texts(test)
    golden_texts = get_texts(golden)

    text_overlaps = {
        "train-val": train_texts.intersection(val_texts),
        "train-test": train_texts.intersection(test_texts),
        "train-golden": train_texts.intersection(golden_texts),
    }

    # 3. Generate Report
    report = ["# FINAL LEAKAGE AUDIT REPORT\n"]
    
    report.append("## 1. Conversation ID Overlap")
    for pair, leaked in overlaps.items():
        report.append(f"- {pair}: {len(leaked)} leaks")
    
    report.append("\n## 2. Textual Overlap (Exact Match)")
    for pair, leaked in text_overlaps.items():
        report.append(f"- {pair}: {len(leaked)} leaks")
    
    # Final Verdict
    all_leaks = sum(len(v) for v in overlaps.values()) + sum(len(v) for v in text_overlaps.values())
    verdict = "PASS" if all_leaks == 0 else "FAIL"
    report.append(f"\n**FINAL VERDICT: {verdict}**\n")
    report.append(f"Total leaks found: {all_leaks}")

    with open("artifacts/FINAL_LEAKAGE_AUDIT.md", "w") as f:
        f.write("\n".join(report))
    
    logger.info(f"Audit complete. Verdict: {verdict}. Report saved to artifacts/FINAL_LEAKAGE_AUDIT.md")

if __name__ == "__main__":
    run_comprehensive_audit()
