import logging

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_majority_baseline(gs_path):
    df = pd.read_csv(gs_path)
    majority_class = df['gold_intent'].mode()[0]
    preds = [majority_class] * len(df)

    acc = accuracy_score(df['gold_intent'], preds)
    f1 = f1_score(df['gold_intent'], preds, average='macro')

    return acc, f1

def run_tfidf_baseline(gs_path):
    gs_df = pd.read_csv(gs_path)

    from sklearn.model_selection import train_test_split
    train, test = train_test_split(gs_df, test_size=0.2, random_state=42)

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

if __name__ == "__main__":
    gs_path = 'evaluation/golden_set.csv'

    maj_acc, maj_f1 = run_majority_baseline(gs_path)
    logger.info(f"Majority Baseline: Acc={maj_acc:.4f}, F1={maj_f1:.4f}")

    try:
        tfidf_acc, tfidf_f1 = run_tfidf_baseline(gs_path)
        logger.info(f"TF-IDF Baseline: Acc={tfidf_acc:.4f}, F1={tfidf_f1:.4f}")
    except Exception as e:
        logger.error(f"TF-IDF Baseline failed: {e}")
