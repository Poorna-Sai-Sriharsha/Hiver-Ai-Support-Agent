import pandas as pd

# Load dataset
df = pd.read_csv('evaluation/golden_set.csv')

# Define mapping from old labels to current taxonomy
mapping = {
    'Delivery & Shipping': 'Order & Logistics',
    'Order Status & Tracking': 'Order & Logistics',
    'Customer Service Access': 'General Inquiry',
    'Account & Security': 'Account Access',
    'Payment & Billing': 'Billing & Subscriptions',
    'Severe Complaint / Fraud': 'General Inquiry',
    'Refunds & Returns': 'Order & Logistics',
    'Product Quality & Warranty': 'Warranty & Repairs'
}

# Apply mapping
df['gold_intent'] = df['gold_intent'].map(mapping).fillna(df['gold_intent'])

# Save back to CSV
df.to_csv('evaluation/golden_set.csv', index=False)
print("Golden set labels aligned with current taxonomy.")
