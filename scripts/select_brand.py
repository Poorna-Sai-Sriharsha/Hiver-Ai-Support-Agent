import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def select_brand(file_path: str):
    """
    Analyzes brands and selects the best one for the support agent.
    Criteria:
    1. High volume of brand responses.
    2. High ratio of pairs (customer message followed by brand response).
    3. Diversity (number of unique customer users).
    """
    if not os.path.exists(file_path):
        logger.error(f"Dataset not found at {file_path}")
        return

    logger.info(f"Analyzing brands from {file_path}...")
    # To avoid loading 2.8M rows multiple times, we load once.
    df = pd.read_csv(file_path)

    # Identify brands (those who are not inbound)
    brands = df[df['inbound'] == False]['author_id'].unique()

    brand_metrics = []

    for brand in brands:
        # Get all tweets by this brand
        brand_tweets = df[df['author_id'] == brand]

        # A "resolved pair" is a customer tweet that was responded to by this brand
        # Check 'in_response_to_tweet_id' for the brand's tweets
        responded_to_ids = set(brand_tweets['in_response_to_tweet_id'].dropna())

        # Count how many of these responded-to tweets actually exist in the dataset as customer tweets
        # (This is a basic proxy for usability)
        pair_count = len(responded_to_ids.intersection(set(df['tweet_id'])))

        # Diversity: unique customers who interacted with this brand
        # We find customers who were responded to by this brand
        customers = df[df['tweet_id'].isin(responded_to_ids)]['author_id'].nunique()

        brand_metrics.append({
            "brand": brand,
            "response_count": len(brand_tweets),
            "pair_count": pair_count,
            "customer_diversity": customers
        })

    # Convert to DataFrame for sorting
    metrics_df = pd.DataFrame(brand_metrics)

    # Sort by pair_count as the primary metric
    metrics_df = metrics_df.sort_values(by="pair_count", ascending=False).reset_index(drop=True)

    # Save candidate brands
    metrics_df.to_csv("brand_candidates.csv", index=False)

    # Selection Logic:
    # We want a brand with a high pair_count (at least 1000+) and good diversity.
    # Typically, the top 1-3 are safe.
    selected_brand = metrics_df.iloc[0]['brand']

    logger.info(f"Selected Brand: {selected_brand}")
    logger.info(f"Pairs available: {metrics_df.iloc[0]['pair_count']}")

    # Update config.yaml
    import yaml
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    config['brand'] = {
        "name": selected_brand,
        "stats": metrics_df.iloc[0].to_dict()
    }

    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    # Save selection justification
    with open("BRAND_SELECTION.md", "w") as f:
        f.write("# Brand Selection Report\n\n")
        f.write(f"**Selected Brand:** {selected_brand}\n\n")
        f.write("## Selection Criteria\n")
        f.write("The brand was selected based on the following metrics:\n")
        f.write(f"- **Total Responses:** {metrics_df.iloc[0]['response_count']}\n")
        f.write(f"- **Usable Pairs (Customer $\rightarrow$ Brand):** {metrics_df.iloc[0]['pair_count']}\n")
        f.write(f"- **Customer Diversity:** {metrics_df.iloc[0]['customer_diversity']}\n\n")
        f.write("## Top Candidates\n")
        f.write(metrics_df.head(10).to_markdown())

if __name__ == "__main__":
    DATA_PATH = "data/twcs.csv"
    select_brand(DATA_PATH)
