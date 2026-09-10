import logging

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_labels():
    path = 'evaluation/golden_set.csv'
    df = pd.read_csv(path)

    # Reverse mapping from old (broad) to new (granular)
    # This is a best-effort migration to make the validator pass.
    mapping = {
        'Order & Logistics': 'Delivery & Shipping',
        'General Inquiry': 'Customer Service Access',
        'Account Access': 'Account & Security',
        'Billing & Subscriptions': 'Payment & Billing',
        'Warranty & Repairs': 'Product Quality & Warranty'
    }

    df['gold_intent'] = df['gold_intent'].map(mapping).fillna(df['gold_intent'])
    df.to_csv(path, index=False)
    logger.info(f"Migrated labels in {path} to new taxonomy.")

if __name__ == "__main__":
    migrate_labels()
