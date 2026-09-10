import pandas as pd

from src.preprocessing.dataset_processor import DatasetProcessor
from src.retrieval.vector_store import VectorStore


def test_preprocessing_cleaning():
    processor = DatasetProcessor(brand_id="TestBrand")
    text = "@User hello https://test.com RT: This is a test!!"
    cleaned, raw = processor.cleaner.clean(text)
    assert "[USER]" in cleaned
    assert "[URL]" in cleaned
    assert "RT:" not in cleaned
    assert "!!" not in cleaned

def test_vector_store_fallback():
    # Test the keyword fallback by creating a store without a model
    vs = VectorStore()
    vs.model = None # Force fallback

    data = pd.DataFrame({
        'customer_message': ["my battery is dead", "i lost my password"],
        'historical_brand_response': ["charge it", "reset it"],
        'metadata': [{}] * 2
    })
    vs.index_data(data)

    results = vs.retrieve("battery dead", k=1)
    assert "charge it" in results[0]['brand_response']

def test_reconstruction_schema():
    processor = DatasetProcessor(brand_id="Apple")
    df = pd.DataFrame({
        'tweet_id': [1, 2],
        'author_id': ["User1", "Apple"],
        'inbound': [True, False],
        'created_at': ["2023-01-01 10:00", "2023-01-01 10:05"],
        'text': ["Help", "Hello"],
        'in_response_to_tweet_id': [None, 1]
    })
    normalized = processor.load_and_reconstruct_df(df)
    assert 'conversation_id' in normalized.columns
    assert normalized.iloc[0]['author_type'] == 'CUSTOMER'
    assert normalized.iloc[1]['author_type'] == 'BRAND'
