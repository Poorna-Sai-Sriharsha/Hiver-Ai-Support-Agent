import logging

import numpy as np

# Try to use sentence-transformers for high-quality embeddings
try:
    from sentence_transformers import SentenceTransformer, util
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    A lightweight vector store for historical support resolutions.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.queries = []
        self.responses = []
        self.embeddings = None

        if HAS_SENTENCE_TRANSFORMERS:
            logger.info(f"Initializing SentenceTransformer with model {model_name}...")
            self.model = SentenceTransformer(model_name)
        else:
            logger.warning("sentence-transformers not installed. Falling back to basic keyword retrieval.")
            self.model = None

    def index_data(self, pairs: list[tuple[str, str]]):
        """
        Indexes Query-Response pairs into the knowledge base.
        """
        if not pairs:
            logger.warning("No data provided to index.")
            return

        self.queries = [p[0] for p in pairs]
        self.responses = [p[1] for p in pairs]

        if HAS_SENTENCE_TRANSFORMERS:
            logger.info(f"Generating embeddings for {len(self.queries)} queries...")
            self.embeddings = self.model.encode(self.queries, convert_to_tensor=True)
        else:
            self.embeddings = None

    def retrieve(self, query: str, k: int = 3) -> list[tuple[str, float]]:
        """
        Retrieves the top-k most similar historical resolutions.
        Returns a list of (response, score).
        """
        if not self.queries:
            return []

        if HAS_SENTENCE_TRANSFORMERS and self.embeddings is not None:
            query_embedding = self.model.encode(query, convert_to_tensor=True)
            cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]

            top_results = np.argsort(-cos_scores.cpu().numpy())[:k]

            results = []
            for idx in top_results:
                results.append((self.responses[idx], float(cos_scores[idx])))
            return results
        else:
            # Basic keyword overlap fallback
            logger.info("Using keyword overlap retrieval...")
            query_words = set(query.lower().split())
            scores = []
            for q in self.queries:
                q_words = set(q.lower().split())
                overlap = len(query_words.intersection(q_words)) / max(len(query_words), 1)
                scores.append(overlap)

            top_results = np.argsort(-np.array(scores))[:k]
            return [(self.responses[idx], scores[idx]) for idx in top_results]
