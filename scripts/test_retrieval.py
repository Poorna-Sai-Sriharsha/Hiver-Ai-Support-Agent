import pandas as pd

from src.retrieval.vector_store import VectorStore


def test_keyword_fallback():
    # Create a small DF
    df = pd.DataFrame({
        'customer_message': ['My order is late', 'I want a refund', 'How to login'],
        'historical_brand_response': ['We are sorry', 'Check your email', 'Use the reset link'],
        'metadata': [{}, {}, {}]
    })
    
    # Force no model by passing a wrong model name or letting it fail
    vs = VectorStore(model_name='non_existent_model')
    vs.model = None # Force fallback
    vs.index_data(df)
    
    res = vs.retrieve("order late", k=1)
    print(f"Query 'order late' -> {res[0]['customer_message']} (Expected: My order is late)")
    
    res = vs.retrieve("refund me", k=1)
    print(f"Query 'refund me' -> {res[0]['customer_message']} (Expected: I want a refund)")

if __name__ == "__main__":
    test_keyword_fallback()
