import logging
import os

import yaml

from src.intent.ai_classifier import AIIntentClassifier
from src.utils.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)

os.environ['LLM_PROVIDER'] = 'ollama'
os.environ['OLLAMA_MODEL'] = 'qwen2.5:7b-instruct'

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

llm = LLMClient()
classifier = AIIntentClassifier(llm, config)

text = 'Hello'
print(f"Classifying text: {text}")
# Manually calling LLM to see if it's the prompt
prompt = "Classify this text: " + text
print("Calling LLM with simple prompt...")
print(llm.call(prompt))
print("Now calling classifier.classify()...")
result = classifier.classify(text)
print(f"Result: {result}")
