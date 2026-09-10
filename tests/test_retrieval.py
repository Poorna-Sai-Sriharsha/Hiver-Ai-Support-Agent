import pandas as pd

from src.retrieval.vector_store import VectorStore


def test_vector_store_indexing():
    vs = VectorStore()
    df = pd.DataFrame({
        'customer_message': ['Where is my order?', 'How to return?'],
        'historical_brand_response': ['It is coming.', 'Go to settings.'],
        'tweet_id': ['1', '2']
    })
    vs.index_data(df)
    assert len(vs.data) == 2

def test_vector_store_retrieve_empty():
    vs = VectorStore()
    res = vs.retrieve("test")
    assert res == []

def test_vector_store_keyword_fallback():
    # Force fallback by removing model
    vs = VectorStore()
    vs.model = None
    df = pd.DataFrame({
        'customer_message': ['The package is lost', 'I want a refund'],
        'historical_brand_response': ['Sorry', 'Okay'],
        'tweet_id': ['1', '2']
    })
    vs.index_data(df)
    res = vs.retrieve("lost package")
    assert res[0]['customer_message'] == 'The package is lost'
    assert res[0]['score'] > 0

def test_leakage_verification():
    vs = VectorStore()
    df = pd.DataFrame({
        'customer_message': ['Msg 1', 'Msg 2'],
        'historical_brand_response': ['Res 1', 'Res 2'],
        'tweet_id': ['T1', 'T2']
    })
    vs.index_data(df)

    # No leak
    assert vs.verify_no_leakage(['T3']) == []
    # Leak
    assert 'T1' in vs.verify_no_leakage(['T1', 'T3'])
