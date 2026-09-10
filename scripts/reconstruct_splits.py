import json
import logging
import os
import random
from collections import defaultdict

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_conversation_roots(df):
    parent_map = df.set_index('tweet_id')['in_response_to_tweet_id'].to_dict()
    root_map = {}

    def find_root(tid):
        if tid in root_map:
            return root_map[tid]
        visited = {tid}
        curr = tid
        while True:
            parent = parent_map.get(curr)
            if parent is None or parent == curr or parent not in parent_map or parent in visited:
                break
            curr = parent
            visited.add(curr)
        root_map[tid] = curr
        return curr

    return [find_root(tid) for tid in df['tweet_id']]

def reconstruct():
    raw_path = 'data/twcs.csv'
    brand_id = 'AmazonHelp'
    
    if not os.path.exists(raw_path):
        logger.error(f"Raw data not found: {raw_path}")
        return

    logger.info(f"Loading raw data and filtering for brand {brand_id}...")
    df = pd.read_csv(raw_path)
    df['tweet_id'] = df['tweet_id'].astype(float)
    df['in_response_to_tweet_id'] = df['in_response_to_tweet_id'].astype(float)
    
    # Filter for conversations that involve AmazonHelp
    # A conversation involves the brand if any tweet in it has author_id == brand_id
    brand_tweets = df[df['author_id'] == brand_id]
    brand_tweet_ids = set(brand_tweets['tweet_id'])
    
    # To correctly identify the whole conversation, we need to find all tweets linked to these brand tweets
    # We can use the connected components approach again
    adj = defaultdict(set)
    for tid, parent in df.set_index('tweet_id')['in_response_to_tweet_id'].to_dict().items():
        if parent != tid and not pd.isna(parent):
            adj[tid].add(parent)
            adj[parent].add(tid)
    
    brand_conv_ids = set()
    for tid in brand_tweet_ids:
        if tid not in brand_conv_ids:
            # BFS to find all linked tweets
            visited = {tid}
            stack = [tid]
            while stack:
                curr = stack.pop()
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        stack.append(neighbor)
            brand_conv_ids.update(visited)
            
    # Filter df to only include these conversations
    df_brand = df[df['tweet_id'].isin(brand_conv_ids)].copy()
    
    # Now we need to assign a unique ID to each conversation
    # We can use the root_id logic on this smaller subset
    df_brand['conversation_id'] = get_conversation_roots(df_brand)
    
    # Aggregate to (customer, brand) pairs
    logger.info("Aggregating conversations...")
    df_brand = df_brand.sort_values('created_at')
    cust_df = df_brand[df_brand['inbound'] == True].drop_duplicates('conversation_id', keep='first')
    brand_df = df_brand[df_brand['inbound'] == False].drop_duplicates('conversation_id', keep='last')
    pairs_df = pd.merge(cust_df[['conversation_id', 'text', 'tweet_id']], 
                       brand_df[['conversation_id', 'text']], 
                       on='conversation_id', how='inner')
    pairs_df.columns = ['conversation_id', 'customer_message', 'tweet_id', 'historical_brand_response']
    
    all_conv_ids = pairs_df['conversation_id'].tolist()
    random.seed(42)
    random.shuffle(all_conv_ids)
    
    golden_size = 169
    test_size = 169
    val_size = 169
    
    golden_ids = all_conv_ids[:golden_size]
    test_ids = all_conv_ids[golden_size : golden_size + test_size]
    val_ids = all_conv_ids[golden_size + test_size : golden_size + test_size + val_size]
    train_ids = all_conv_ids[golden_size + test_size + val_size:]
    
    logger.info(f"New Split Sizes: Golden={len(golden_ids)}, Test={len(test_ids)}, Val={len(val_ids)}, Train={len(train_ids)}")
    
    meta = {
        "brand": brand_id,
        "total_conversations": len(all_conv_ids),
        "train_size": len(train_ids),
        "val_size": len(val_ids),
        "test_size": len(test_ids),
        "train_conv_ids": train_ids,
        "val_conv_ids": val_ids,
        "test_conv_ids": test_ids,
        "golden_conv_ids": golden_ids
    }
    with open('data/processed/split_metadata.json', 'w') as f:
        json.dump(meta, f, indent=4)
    
    pairs_df[pairs_df['conversation_id'].isin(train_ids)].to_csv('data/processed/train.csv', index=False)
    pairs_df[pairs_df['conversation_id'].isin(val_ids)].to_csv('data/processed/val.csv', index=False)
    pairs_df[pairs_df['conversation_id'].isin(test_ids)].to_csv('data/processed/test.csv', index=False)
    
    golden_df = pairs_df[pairs_df['conversation_id'].isin(golden_ids)].copy()
    golden_df['is_annotated'] = False
    golden_df['gold_intent'] = None
    golden_df['should_escalate'] = None
    golden_df['escalation_reason'] = None
    golden_df['severity'] = None
    golden_df['expected_response_points'] = None
    golden_df['annotation_confidence'] = 1.0
    golden_df['annotator_notes'] = None
    golden_df['annotation_timestamp'] = None
    golden_df.to_csv('evaluation/annotation_queue.csv', index=False)
    
    logger.info("All splits and golden set reconstructed successfully.")

if __name__ == "__main__":
    reconstruct()
