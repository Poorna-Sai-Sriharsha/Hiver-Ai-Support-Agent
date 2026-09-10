import json
import logging
import os

from src.retrieval.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_leakage_audit():
    meta_path = 'data/processed/split_metadata.json'
    if not os.path.exists(meta_path):
        logger.error(f"Metadata not found at {meta_path}")
        return

    with open(meta_path, 'r') as f:
        meta = json.load(f)

    train_convs = set(meta['train_conv_ids'])
    val_convs = set(meta['val_conv_ids'])
    test_convs = set(meta['test_conv_ids'])

    logger.info("--- Conversation Split Audit ---")
    # Check for overlaps in the metadata itself
    overlaps = {
        "train-val": train_convs.intersection(val_convs),
        "train-test": train_convs.intersection(test_convs),
        "val-test": val_convs.intersection(test_convs),
    }

    for pair, leaked in overlaps.items():
        logger.info(f"{pair}: {len(leaked)} leaks")

    # Retrieval Index Leakage
    try:
        vs = VectorStore()
        vs.load('data/vector_index.pkl')

        # In the VectorStore, the data is a list of records.
        # We need to check if any conversation_id from test/val is in the store.
        # The VectorStore doesn't explicitly store conversation_id in its retrieve results,
        # but the internal self.data does (if it was passed in).

        # Let's check the actual data in the index
        index_convs = set()
        for item in vs.data:
            # Look for conversation_id in metadata or root
            cid = item.get('conversation_id') or item.get('metadata', {}).get('conversation_id')
            if cid is not None:
                index_convs.add(cid)

        forbidden = val_convs.union(test_convs)
        leaks = index_convs.intersection(forbidden)
        logger.info(f"Retrieval Index Leakage (Conversations): {len(leaks)} leaks")
        if leaks:
            logger.error(f"LEAKED CONVERSATIONS: {list(leaks)[:10]}")

    except Exception as e:
        logger.error(f"Could not audit retrieval index: {e}")

if __name__ == "__main__":
    run_leakage_audit()
