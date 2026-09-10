import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_leakage():
    train_path = 'data/processed/train.csv'
    val_path = 'data/processed/val.csv'
    test_path = 'data/processed/test.csv'
    golden_path = 'evaluation/annotation_queue.csv'
    
    if not all(os.path.exists(p) for p in [train_path, val_path, test_path, golden_path]):
        logger.error("Missing files for leakage fix.")
        return

    train = pd.read_csv(train_path)
    val = pd.read_csv(val_path)
    test = pd.read_csv(test_path)
    golden = pd.read_csv(golden_path)

    # 1. Remove Golden Set from Test Set
    golden_ids = set(golden['conversation_id'].astype(str))
    test_ids = set(test['conversation_id'].astype(str))
    leaked_ids = golden_ids.intersection(test_ids)
    
    logger.info(f"Removing {len(leaked_ids)} golden set leaks from test set...")
    test = test[~test['conversation_id'].astype(str).isin(leaked_ids)]
    
    # 2. Remove Textual Duplicates
    all_data = pd.concat([
        train.assign(split='train'),
        val.assign(split='val'),
        test.assign(split='test')
    ])
    
    duplicates = all_data[all_data.duplicated('customer_message', keep=False)]
    unique_texts = set(duplicates['customer_message'].unique())
    
    logger.info(f"Found {len(unique_texts)} text-based duplicate messages across splits.")
    
    seen_texts = set()
    
    def filter_data(df):
        nonlocal seen_texts
        filtered = []
        for _, row in df.iterrows():
            text = row['customer_message']
            if text not in unique_texts or text not in seen_texts:
                filtered.append(row)
                seen_texts.add(text)
        return pd.DataFrame(filtered)

    # Need to use a closure or just process them sequentially
    # Let's just do it sequentially to avoid nonlocal issues with function definitions in this scope
    
    final_train = []
    for _, row in train.iterrows():
        text = row['customer_message']
        if text not in unique_texts or text not in seen_texts:
            final_train.append(row)
            seen_texts.add(text)
            
    final_val = []
    for _, row in val.iterrows():
        text = row['customer_message']
        if text not in unique_texts or text not in seen_texts:
            final_val.append(row)
            seen_texts.add(text)
            
    final_test = []
    for _, row in test.iterrows():
        text = row['customer_message']
        if text not in unique_texts or text not in seen_texts:
            final_test.append(row)
            seen_texts.add(text)
            
    train = pd.DataFrame(final_train)
    val = pd.DataFrame(final_val)
    test = pd.DataFrame(final_test)
    
    logger.info(f"Final sizes: Train={len(train)}, Val={len(val)}, Test={len(test)}")
    
    train.to_csv(train_path, index=False)
    val.to_csv(val_path, index=False)
    test.to_csv(test_path, index=False)
    
    logger.info("Leakage fix complete.")

if __name__ == "__main__":
    fix_leakage()
