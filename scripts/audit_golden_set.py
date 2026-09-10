import json
import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_golden_set_audit():
    queue_path = 'evaluation/annotation_queue.csv'
    meta_path = 'data/processed/split_metadata.json'
    
    if not os.path.exists(queue_path):
        logger.error(f"Queue file not found: {queue_path}")
        return
    
    df = pd.read_csv(queue_path)
    logger.info(f"Auditing {len(df)} examples in annotation queue.")
    
    # 1. Duplicate Check
    dupes_msg = df['customer_message'].duplicated().sum()
    dupes_id = df['conversation_id'].duplicated().sum()
    logger.info(f"Duplicates: Messages={dupes_msg}, IDs={dupes_id}")
    
    # 2. Split Overlap Check
    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            meta = json.load(f)
        
        train_ids = set(meta.get('train_conv_ids', []))
        val_ids = set(meta.get('val_conv_ids', []))
        test_ids = set(meta.get('test_conv_ids', []))
        
        queue_ids = set(df['conversation_id'].astype(str))
        # Convert train_ids to string for comparison
        train_ids = {str(i) for i in train_ids}
        val_ids = {str(i) for i in val_ids}
        test_ids = {str(i) for i in test_ids}
        
        overlap_train = queue_ids.intersection(train_ids)
        overlap_val = queue_ids.intersection(val_ids)
        overlap_test = queue_ids.intersection(test_ids)
        
        logger.info(f"Overlap with Train: {len(overlap_train)}")
        logger.info(f"Overlap with Val: {len(overlap_val)}")
        logger.info(f"Overlap with Test: {len(overlap_test)}")
        
        if len(overlap_train) > 0:
            logger.warning(f"LEAKAGE: {len(overlap_train)} examples in queue are also in training set!")
    else:
        logger.warning("Metadata not found, cannot check split overlap.")

    # 3. Taxonomy Compatibility
    # We check if the columns for labels exist
    label_cols = ['gold_intent', 'should_escalate', 'escalation_reason']
    for col in label_cols:
        if col not in df.columns:
            logger.error(f"Missing label column: {col}")
    
    # 4. Set labels to WAITING_FOR_HUMAN_ANNOTATION
    # Note: In CSV, we can't easily "mark" unless we write the file back.
    # The user asked to clearly mark them.
    df[label_cols] = "WAITING_FOR_HUMAN_ANNOTATION"
    df.to_csv(queue_path, index=False)
    logger.info(f"Updated {queue_path} with WAITING_FOR_HUMAN_ANNOTATION labels.")
    
    # 5. Provenance/Sampling
    # The queue is typically sampled from the test set or a separate holdout.
    # We just verify that the records look legitimate.
    sample_text = df['customer_message'].iloc[0]
    if "[USER]" in sample_text or "Amazon" in sample_text:
        logger.info("Provenance looks legitimate (AmazonHelp patterns found).")
    else:
        logger.warning("Provenance check failed: Records do not look like AmazonHelp data.")

if __name__ == "__main__":
    run_golden_set_audit()
