import os

import pandas as pd
import yaml

from src.intent.ai_classifier import AIIntentClassifier
from src.utils.llm_client import LLMClient

# Setup
os.environ['LLM_PROVIDER'] = 'ollama'
os.environ['OLLAMA_MODEL'] = 'qwen2.5:7b-instruct'

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

llm = LLMClient()
classifier = AIIntentClassifier(llm, config)
golden_set = pd.read_csv('evaluation/golden_set.csv')

print(f"Taxonomy: {config['intents']}\n")
print(f"{'Gold Intent':<30} | {'Predicted Intent':<30} | {'Message'}")
print("-" * 90)

for i, row in golden_set.head(20).iterrows():
    text = row['customer_message']
    gold = row['gold_intent']
    pred = classifier.classify(text)['intent']
    print(f"{gold:<30} | {pred:<30} | {text[:50]}...")
