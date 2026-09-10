import numpy as np
import pandas as pd

df = pd.read_csv('data/twcs.csv')
df['tweet_id'] = df['tweet_id'].astype(float)
df['in_response_to_tweet_id'] = df['in_response_to_tweet_id'].astype(float)

# Vectorized root finding (approximate but fast)
# We'll iterate a few times to propagate the root
roots = df['tweet_id'].values.copy()
parents = df.set_index('tweet_id')['in_response_to_tweet_id'].to_dict()

for _ in range(5): # Most threads are short
    new_roots = []
    for r in roots:
        p = parents.get(r)
        if p is not None and p != r:
            new_roots.append(p)
        else:
            new_roots.append(r)
    roots = np.array(new_roots)

df['conversation_id'] = roots

convs = df.groupby('conversation_id')
total = len(convs)

# Using boolean flags
has_cust = df[df['inbound'] == True]['conversation_id'].nunique()
has_brand = df[df['inbound'] == False]['conversation_id'].nunique()

# Conversations that have both
cust_ids = set(df[df['inbound'] == True]['conversation_id'])
brand_ids = set(df[df['inbound'] == False]['conversation_id'])
has_both = len(cust_ids.intersection(brand_ids))

print(f"Total Conversations: {total}")
print(f"Has Customer: {has_cust}")
print(f"Has Brand: {has_brand}")
print(f"Has Both: {has_both}")
