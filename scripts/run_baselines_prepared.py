import json
import logging
import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_majority_baseline(df):
    if df.empty or 'gold_intent' not in df.columns:
        return None, None
    majority_class = df['gold_intent'].mode()[0]
    preds = [majority_class] * len(df)
    acc = accuracy_score(df['gold_intent'], preds)
    f1 = f1_score(df['gold_intent'], preds, average='macro')
    return acc, f1

def run_tfidf_baseline(df):
    if df.empty or 'gold_intent' not in df.columns:
        return None, None
    
    from sklearn.model_selection import train_test_split
    # Split to simulate realistic performance
    train, test = train_test_split(df, test_size=0.2, random_state=42)
    
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_train = vectorizer.fit_transform(train['customer_message'])
    y_train = train['gold_intent']
    X_test = vectorizer.transform(test['customer_message'])
    y_test = test['gold_intent']
    
    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average='macro')
    return acc, f1

def main():
    gs_path = 'evaluation/golden_set.csv'
    if not os.path.exists(gs_path):
        logger.error("Golden set not found. Baselines cannot run.")
        return

    df = pd.read_csv(gs_path)
    
    # Check if human labels exist
    if df['gold_intent'].isnull().any() or (df['gold_intent'] == "WAITING_FOR_HUMAN_ANNOTATION").any():
        logger.info("Golden set is not yet human-labelled. Baselines are READY but will not produce final metrics.")
        return

    maj_acc, maj_f1 = run_majority_baseline(df)
    tfidf_acc, tfidf_f1 = run_tfidf_baseline(df)
    
    results = {
        "majority": {"accuracy": maj_acc, "f1": maj_f1},
        "tfidf": {"accuracy": tfidf_acc, "f1": tfidf_f1}
    }
    
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/baseline_metrics.json", "w") as f:
        json.dump(results, f, indent=4)
    
    logger.info("Baselines executed successfully.")

if __name__ == "__main__":
    main()
