import json
import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def profile_dataset(file_path: str):
    """
    Performs a deep profile of the Customer Support on Twitter dataset.
    Outputs: data_profile.json and DATA_PROFILE.md.
    """
    if not os.path.exists(file_path):
        logger.error(f"Dataset not found at {file_path}")
        return

    logger.info(f"Profiling dataset at {file_path}...")
    df = pd.read_csv(file_path)

    # 1. Basic Statistics
    profile = {
        "basic_stats": {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
        }
    }

    # 2. Tweet Relationships & Types
    # Inbound = True (Customer), False (Brand)
    if 'inbound' in df.columns:
        profile["tweet_types"] = {
            "customer_tweets": int((df['inbound'] == True).sum()),
            "brand_tweets": int((df['inbound'] == False).sum()),
        }

    # 3. Brand Analysis
    if 'author_id' in df.columns:
        # Brand is likely the one with inbound=False
        brand_counts = df[df['inbound'] == False]['author_id'].value_counts()
        profile["brand_stats"] = {
            "total_brands": len(brand_counts),
            "brands_distribution": brand_counts.to_dict(),
        }

    # 4. Conversation Analysis
    # A conversation is often linked by 'in_response_to_tweet_id'
    # We can try to estimate conversation count by finding root tweets
    if 'in_response_to_tweet_id' in df.columns:
        roots = df[df['in_response_to_tweet_id'].isna()]
        profile["conversation_stats"] = {
            "estimated_root_tweets": len(roots),
        }

    # 5. Noise Analysis
    if 'text' in df.columns:
        # Sample text to check for URLs, Mentions, etc.
        sample_text = " ".join(df['text'].astype(str).head(1000).tolist())
        profile["noise_stats"] = {
            "has_urls": "http" in sample_text,
            "has_mentions": "@" in sample_text,
            "has_hashtags": "#" in sample_text,
        }

    # Save JSON
    with open("data_profile.json", "w") as f:
        json.dump(profile, f, indent=4)

    # Generate Markdown Report
    with open("DATA_PROFILE.md", "w") as f:
        f.write("# Data Profile: Customer Support on Twitter\n\n")
        f.write(f"**Total Rows:** {profile['basic_stats']['row_count']}\n")
        f.write(f"**Total Columns:** {profile['basic_stats']['column_count']}\n\n")

        f.write("## Column Analysis\n")
        f.write("| Column | Missing Values |\n|---|---|\n")
        f.writelines(f"| {col} | {miss} |\n" for col, miss in profile['basic_stats']['missing_values'].items())

        f.write(f"\n**Duplicate Rows:** {profile['basic_stats']['duplicate_rows']}\n\n")

        if "tweet_types" in profile:
            f.write("## Tweet Distribution\n")
            f.write(f"- Customer Messages: {profile['tweet_types']['customer_tweets']}\n")
            f.write(f"- Brand Responses: {profile['tweet_types']['brand_tweets']}\n\n")

        if "brand_stats" in profile:
            f.write("## Brand Analysis\n")
            f.write(f"- Total Brands identified: {profile['brand_stats']['total_brands']}\n")
            f.write("\nTop Brands by Response Volume:\n")
            sorted_brands = sorted(profile['brand_stats']['brands_distribution'].items(), key=lambda x: x[1], reverse=True)[:10]
            f.writelines(f"- {b}: {c} responses\n" for b, c in sorted_brands)

    logger.info("Profiling complete. Artifacts created: data_profile.json, DATA_PROFILE.md")

if __name__ == "__main__":
    # Expected path for the real dataset
    DATA_PATH = "data/twcs.csv"
    profile_dataset(DATA_PATH)
