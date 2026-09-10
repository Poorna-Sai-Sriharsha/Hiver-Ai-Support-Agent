import json
import logging
import os
import time

import pandas as pd
import psutil

from src.agent import SupportAgent
from src.preprocessing.dataset_processor import DatasetProcessor
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def measure_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) # MB

def run_performance_audit():
    logger.info("Starting Performance and Memory Audit...")
    
    # 1. Preprocessing Memory/Time
    # Note: train.csv is already reconstructed, so we simulate a raw load for memory check
    # But since we don't have the raw file here, we'll verify the reconstruction logic
    # on the processed df by simulating the mapping.
    start_mem = measure_memory()
    start_time = time.time()
    
    processor = DatasetProcessor(brand_id="TestBrand")
    # Mock a raw-style dataframe for load_and_reconstruct_df
    mock_raw = pd.DataFrame({
        'tweet_id': range(1000),
        'in_response_to_tweet_id': [None] * 1000,
        'author_id': ["User"] * 1000,
        'inbound': [True] * 1000,
        'created_at': ["2023-01-01 10:00"] * 1000,
        'text': ["Help message"] * 1000
    })
    
    processor.load_and_reconstruct_df(mock_raw)
    
    end_time = time.time()
    end_mem = measure_memory()
    
    prep_results = {
        "time_sec": end_time - start_time,
        "mem_delta_mb": end_mem - start_mem
    }
    logger.info(f"Preprocessing (1k rows): {prep_results}")

    # 2. Indexing Time
    start_time = time.time()
    kb = VectorStore()
    # Use a subset of the processed train set
    try:
        train_df = pd.read_csv('data/processed/train.csv').head(100)
        # The indexer expects customer_message and historical_brand_response
        kb.index_data(train_df)
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        index_time = -1
    else:
        end_time = time.time()
        index_time = end_time - start_time
    
    logger.info(f"Indexing (100 rows): {index_time:.4f}s")

    # 3. Retrieval Latency
    try:
        agent = SupportAgent("config/config.yaml", kb, LLMClient())
        latencies = []
        for i in range(10):
            t0 = time.time()
            agent.kb.retrieve("My package is missing", k=3)
            latencies.append(time.time() - t0)
        avg_latency = sum(latencies) / len(latencies)
    except Exception as e:
        logger.error(f"Retrieval latency test failed: {e}")
        avg_latency = -1
        
    logger.info(f"Avg Retrieval Latency: {avg_latency:.4f}s")

    results = {
        "preprocessing": prep_results,
        "indexing_100": index_time,
        "avg_retrieval_latency": avg_latency
    }
    
    with open("artifacts/performance_metrics.json", "w") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    run_performance_audit()
