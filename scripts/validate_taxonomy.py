import logging
import os
import sys

import pandas as pd
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_intents():
    with open('config/intents.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return [i['name'] for i in config['intents']]

def validate_taxonomy():
    valid_intents = load_intents()
    logger.info(f"Valid Intents: {valid_intents}")

    errors = []

    # 1. Check INTENTS.md
    if os.path.exists('INTENTS.md'):
        with open('INTENTS.md', 'r') as f:
            content = f.read()
            for intent in valid_intents:
                if intent not in content:
                    errors.append(f"INTENTS.md: Missing intent {intent}")

    # 2. Check Golden Set
    golden_set_path = 'evaluation/golden_set.csv'
    if os.path.exists(golden_set_path):
        df = pd.read_csv(golden_set_path)
        if 'gold_intent' in df.columns:
            found_intents = df['gold_intent'].unique()
            for intent in found_intents:
                if intent not in valid_intents:
                    errors.append(f"Golden Set: Unknown intent {intent}")
            for intent in valid_intents:
                if intent not in found_intents:
                    logger.warning(f"Golden Set: Intent {intent} not present in data")

    # 3. Check config.yaml (if it has a mapping)
    if os.path.exists('config/config.yaml'):
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
            # Look for any intent-related lists
            for key, value in config.items():
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and any(i in item for i in valid_intents):
                            pass # match

    if errors:
        for err in errors:
            logger.error(err)
        sys.exit(1)
    else:
        logger.info("Taxonomy validation passed!")

if __name__ == "__main__":
    validate_taxonomy()
