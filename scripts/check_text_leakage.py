import json

import pandas as pd

with open('data/processed/split_metadata.json', 'r') as f:
    meta = json.load(f)

train_df = pd.read_csv('data/processed/train.csv')
test_df = pd.read_csv('data/processed/test.csv')

train_texts = set(train_df['customer_message'].astype(str).str.lower().str.strip())
test_texts = set(test_df['customer_message'].astype(str).str.lower().str.strip())

overlap = train_texts.intersection(test_texts)
print(f"Exact text overlap: {len(overlap)}")
for text in list(overlap)[:5]:
    print(f"Example: {text}")
