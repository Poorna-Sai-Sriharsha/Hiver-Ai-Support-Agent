import json
import logging
import os

import numpy as np
import pandas as pd
import yaml

from src.preprocessing.dataset_processor import DatasetProcessor

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def prepare_data(demo_mode: bool = False):
    """
    Full data preparation pipeline: Reconstruction -> Splitting -> Storage.
    """
    # Load config to get the selected brand
    with open("config/config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    brand_id = config['brand']['name']

    data_path = "data/twcs.csv"
    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Reconstruction
    processor = DatasetProcessor(brand_id=brand_id)
    if demo_mode:
        logger.info("Demo mode enabled. Sampling raw data before reconstruction for speed.")
        # Sample 10% of the data to keep it fast but representative
        df_raw = pd.read_csv(data_path).sample(frac=0.1, random_state=42)
        normalized_df = processor.load_and_reconstruct_df(df_raw)
    else:
        normalized_df = processor.load_and_reconstruct(data_path)

    interactions_df = processor.create_interaction_dataset(normalized_df)

    # 2. Leakage-Safe Splitting
    # Requirement: Split at conversation level.
    conv_ids = interactions_df['conversation_id'].unique()
    np.random.seed(42)
    np.random.shuffle(conv_ids)

    # Split ratios: 80% train, 10% val, 10% test
    n_total = len(conv_ids)
    train_end = int(n_total * 0.8)
    val_end = int(n_total * 0.9)

    train_ids = conv_ids[:train_end]
    val_ids = conv_ids[train_end:val_end]
    test_ids = conv_ids[val_end:]

    train_df = interactions_df[interactions_df['conversation_id'].isin(train_ids)]
    val_df = interactions_df[interactions_df['conversation_id'].isin(val_ids)]
    test_df = interactions_df[interactions_df['conversation_id'].isin(test_ids)]

    # 3. Store splits and metadata
    train_df.to_csv(f"{output_dir}/train.csv", index=False)
    val_df.to_csv(f"{output_dir}/val.csv", index=False)
    test_df.to_csv(f"{output_dir}/test.csv", index=False)

    split_metadata = {
        "brand": brand_id,
        "total_conversations": n_total,
        "train_size": len(train_df),
        "val_size": len(val_df),
        "test_size": len(test_df),
        "train_conv_ids": train_ids.tolist(),
        "val_conv_ids": val_ids.tolist(),
        "test_conv_ids": test_ids.tolist(),
    }
    with open(f"{output_dir}/split_metadata.json", "w") as f:
        json.dump(split_metadata, f, indent=4)

    # Create methodology document
    with open("DATA_SPLITTING_METHODOLOGY.md", "w") as f:
        f.write("# Data Splitting Methodology\n\n")
        f.write(f"**Brand:** {brand_id}\n\n")
        f.write("## Leakage Prevention\n")
        f.write("To prevent data leakage, the dataset was split at the **conversation level**.\n")
        f.write("This ensures that if a conversation has multiple interactions, all of them\n")
        f.write("fall into the same split (Train, Val, or Test). A random shuffle of unique\n")
        f.write("conversation IDs was performed with a fixed seed (42) for reproducibility.\n\n")
        f.write("## Split Ratios\n")
        f.write("- Train: 80%\n")
        f.write("- Validation: 10%\n")
        f.write("- Test: 10%\n\n")
        f.write("## Metrics\n")
        f.write(f"- Total Unique Conversations: {n_total}\n")
        f.write(f"- Train Set Size: {len(train_df)} pairs\n")
        f.write(f"- Val Set Size: {len(val_df)} pairs\n")
        f.write(f"- Test Set Size: {len(test_df)} pairs\n")

    logger.info(f"Data preparation complete. Splits saved to {output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Use a sampled subset for faster execution")
    args = parser.parse_args()

    prepare_data(demo_mode=args.demo)
