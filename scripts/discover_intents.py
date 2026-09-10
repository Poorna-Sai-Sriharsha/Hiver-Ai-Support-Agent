import json
import logging
import os

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def discover_intents(train_csv_path: str, n_clusters: int = 10):
    """
    Uses TF-IDF and K-Means clustering to discover potential intents
    from the training set. This is a fallback for when embedding models are unavailable.
    """
    if not os.path.exists(train_csv_path):
        logger.error(f"Train file not found at {train_csv_path}")
        return

    logger.info(f"Loading training data from {train_csv_path}...")
    df = pd.read_csv(train_csv_path)

    # Use only customer messages for intent discovery
    messages = df['customer_message'].astype(str).tolist()

    logger.info(f"Generating TF-IDF vectors for {len(messages)} messages...")
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(messages)

    logger.info(f"Clustering into {n_clusters} groups...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(tfidf_matrix)

    df['cluster'] = clusters

    # For each cluster, find the most frequent words to help identify the intent
    cluster_themes = {}
    feature_names = vectorizer.get_feature_names_out()

    for i in range(n_clusters):
        cluster_indices = np.where(clusters == i)[0]
        if len(cluster_indices) == 0:
            continue

        # Calculate average TF-IDF for this cluster
        cluster_tfidf = tfidf_matrix[cluster_indices].mean(axis=0)
        sorted_indices = np.argsort(cluster_tfidf).flatten()[::-1]
        top_words = [str(feature_names[idx]) for idx in sorted_indices[:10]]

        # Get a few example messages from this cluster
        cluster_msgs = df[df['cluster'] == i]['customer_message'].head(5).tolist()

        cluster_themes[i] = {
            "top_words": top_words,
            "examples": cluster_msgs
        }

    # Save results for manual review
    df.to_csv("intent_discovery_clusters.csv", index=False)
    with open("cluster_examples.json", "w") as f:
        json.dump(cluster_themes, f, indent=4)

    logger.info("Discovery complete. Artifacts created: intent_discovery_clusters.csv, cluster_examples.json")
    return cluster_themes

if __name__ == "__main__":
    TRAIN_PATH = "data/processed/train.csv"
    discover_intents(TRAIN_PATH)
