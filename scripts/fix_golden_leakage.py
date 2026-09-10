import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_leakage():
    test_path = 'data/processed/test.csv'
    golden_path = 'evaluation/annotation_queue.csv'
    output_path = 'data/processed/test_fixed.csv'
    
    if not os.path.exists(test_path) or not os.path.exists(golden_path):
        logger.error("Required files not found.")
        return

    test_df = pd.read_csv(test_path)
    golden_df = pd.read_csv(golden_path)
    
    # Use conversation_id to identify leaks
    golden_ids = set(golden_df['conversation_id'].unique())
    initial_count = len(test_df)
    
    # Remove golden IDs from test set
    fixed_test_df = test_df[~test_df['conversation_id'].isin(golden_ids)]
    final_count = len(fixed_test_df)
    
    leaks_removed = initial_count - final_count
    logger.info(f"Removed {leaks_removed} leaking examples from test set.")
    
    fixed_test_df.to_csv(output_path, index=False)
    
    # Overwrite the original test.csv to apply the fix
    import shutil
    shutil.copy(output_path, test_path)
    os.remove(output_path)
    
    logger.info(f"Test set updated. Final size: {final_count}")

if __name__ == "__main__":
    fix_leakage()
