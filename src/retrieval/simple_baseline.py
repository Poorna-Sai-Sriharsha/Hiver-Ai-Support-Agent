import logging

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleIntentClassifier:
    """
    A non-LLM baseline using TF-IDF and Logistic Regression.
    """
    def __init__(self, train_df: pd.DataFrame):
        # We need labels to train. For this baseline, we'll use a small set of
        # synthetic labels generated from the taxonomy for the training set
        # since the raw dataset is unlabeled.
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.model = LogisticRegression(max_iter=1000)

        # Simulate training labels based on the taxonomy (for baseline purposes)
        # In a real scenario, this would be hand-labeled training data.
        X = self.vectorizer.fit_transform(train_df['customer_message'])
        y = self._generate_simulated_labels(train_df['customer_message'])

        self.model.fit(X, y)

    def _generate_simulated_labels(self, messages):
        # Simple rule-based labeling for the baseline's training set
        labels = []
        for msg in messages:
            msg = str(msg).lower()
            if any(w in msg for w in ["refund", "return"]): labels.append("Refunds & Returns")
            elif any(w in msg for w in ["login", "account", "password"]): labels.append("Account & Security")
            elif any(w in msg for w in ["delivery", "shipping", "late"]): labels.append("Delivery & Shipping")
            elif any(w in msg for w in ["where is", "tracking"]): labels.append("Order Status & Tracking")
            else: labels.append("Delivery & Shipping") # Majority class
        return np.array(labels)

    def predict(self, text: str) -> str:
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]

class SimpleRetrievalSystem:
    """
    A simple BM25-like retrieval system using TF-IDF similarity.
    """
    def __init__(self, historical_df: pd.DataFrame):
        self.df = historical_df
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(historical_df['customer_message'])

    def retrieve(self, query: str, k: int = 1):
        query_vec = self.vectorizer.transform([query])
        similarities = (self.tfidf_matrix @ query_vec.T).toarray().flatten()
        top_idx = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_idx:
            results.append({
                "response": self.df.iloc[idx]['historical_brand_response'],
                "score": similarities[idx]
            })
        return results
