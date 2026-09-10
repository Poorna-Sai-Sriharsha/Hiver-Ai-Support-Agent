import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class VectorStore:
    """
    A production-grade vector store for historical support resolutions.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.data = []  # List of {customer_message, brand_response, metadata}
        self.embeddings = None

        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading SentenceTransformer {model_name}...")
                self.model = SentenceTransformer(model_name)
            except (ImportError, RuntimeError) as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}. Falling back to TF-IDF.")
                self.model = None
        else:
            self.model = None

    def index_data(self, interactions_df: pd.DataFrame):
        """
        Indexes interaction pairs.
        """
        self.data = interactions_df.to_dict('records')

        if self.model:
            logger.info(f"Indexing {len(self.data)} interactions...")
            messages = [item['customer_message'] for item in self.data]
            self.embeddings = self.model.encode(messages, show_progress_bar=True)
        else:
            logger.warning("No embedding model available. Vector search will be disabled.")

    def save(self, path: str):
        """Saves the index to disk."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({'data': self.data, 'embeddings': self.embeddings, 'model_name': self.model_name}, f)
        logger.info(f"Index saved to {path}")

    def load(self, path: str):
        """Loads the index from disk."""
        import pickle
        with open(path, 'rb') as f:
            payload = pickle.load(f)
            self.data = payload['data']
            self.embeddings = payload['embeddings']
            self.model_name = payload['model_name']
        logger.info(f"Index loaded from {path}")

    def verify_no_leakage(self, forbidden_ids: list[str], id_field: str = 'tweet_id') -> list[str]:
        """
        Verifies that no forbidden IDs are present in the index.
        Returns a list of leaked IDs.
        """
        leaked = []
        for item in self.data:
            item_id = item.get(id_field)
            if item_id in forbidden_ids:
                leaked.append(item_id)
        return leaked

    def retrieve(self, query: str, k: int = 3) -> list[dict[str, Any]]:
        """
        Retrieves top-k most similar historical resolutions.
        """
        if not self.data:
            return []

        if self.model and self.embeddings is not None:
            query_emb = self.model.encode([query])
            scores = cosine_similarity(query_emb, self.embeddings)[0]
            top_indices = np.argsort(scores)[::-1][:k]

            results = []
            for idx in top_indices:
                results.append({
                    "score": float(scores[idx]),
                    "customer_message": self.data[idx]['customer_message'],
                    "brand_response": self.data[idx]['historical_brand_response'],
                    "metadata": self.data[idx].get('metadata', {}),
                    "id": self.data[idx].get('tweet_id')
                })
            return results
        else:
            # Fallback to a robust keyword search
            logger.info("Using robust keyword fallback retrieval...")
            results = []

            stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}

            query_words = set(query.lower().split()) - stop_words
            if not query_words:
                query_words = set(query.lower().split())

            scored_data = []
            for item in self.data:
                msg_words = set(item['customer_message'].lower().split()) - stop_words
                intersection = query_words.intersection(msg_words)
                score = len(intersection) / max(len(query_words), 1)
                scored_data.append((score, item))

            scored_data.sort(key=lambda x: x[0], reverse=True)
            for score, item in scored_data[:k]:
                results.append({
                    "score": float(score),
                    "customer_message": item['customer_message'],
                    "brand_response": item['historical_brand_response'],
                    "metadata": item.get('metadata', {}),
                    "id": item.get('tweet_id')
                })
            return results
