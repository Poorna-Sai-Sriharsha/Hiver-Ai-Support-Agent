import pandas as pd

from src.retrieval.vector_store import VectorStore


def test_empty():
    vs = VectorStore()
    vs.model = None
    vs.index_data(pd.DataFrame(columns=['customer_message', 'historical_brand_response']))
    res = vs.retrieve("test", k=1)
    print(f"Empty retrieval -> {res}")

if __name__ == "__main__":
    test_empty()
