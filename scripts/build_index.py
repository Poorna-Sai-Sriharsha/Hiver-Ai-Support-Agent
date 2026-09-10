import logging
import os

import pandas as pd

from src.retrieval.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    train_data_path = 'data/processed/train.csv'
    index_save_path = 'data/vector_index.pkl'

    if not os.path.exists(train_data_path):
        logger.error(f"Train data not found at {train_data_path}")
        return

    logger.info("Loading training data...")
    df = pd.read_csv(train_data_path)

    # The VectorStore expects columns 'customer_message' and 'historical_brand_response'
    # based on the retrieve() method.
    logger.info("Initializing VectorStore and indexing data...")
    vs = VectorStore()
    vs.index_data(df)

    logger.info("Saving vector index...")
    vs.save(index_save_path)
    logger.info(f"Successfully built and saved index to {index_save_path}")

if __name__ == "__main__":
    main()
