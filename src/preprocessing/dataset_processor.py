import logging
import re

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextCleaner:
    """
    Handles normalization of Twitter text without losing critical support meaning.
    """
    def __init__(self):
        # Regex patterns for common Twitter noise
        self.patterns = {
            'mention': r'@\w+',
            'url': r'https?://\S+|www\.\S+',
            'rt': r'\bRT\b',
            'excessive_punct': r'([!?.]){2,}',
        }

    def clean(self, text: str, keep_raw: bool = True) -> tuple[str, str]:
        """
        Cleans text and returns (normalized_text, raw_text).
        """
        if not isinstance(text, str):
            return "", ""

        raw = text
        # Normalization
        text = re.sub(self.patterns['mention'], '[USER]', text)
        text = re.sub(self.patterns['url'], '[URL]', text)
        text = re.sub(self.patterns['rt'], '', text)
        text = re.sub(self.patterns['excessive_punct'], r'\\1', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text, raw

class DatasetProcessor:
    """
    Reconstructs conversations into a normalized internal schema.
    """
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        self.cleaner = TextCleaner()

    def load_and_reconstruct_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Reconstructs conversations from an already loaded DataFrame.
        """
        parent_map = {}
        for tid, parent in zip(df['tweet_id'], df['in_response_to_tweet_id']):
            parent_map[tid] = parent
        return self._reconstruct_from_filtered(df, parent_map)

    def load_and_reconstruct(self, file_path: str) -> pd.DataFrame:
        """
        Loads the raw dataset and transforms it into a normalized conversation schema.
        Implements chunked loading for memory safety.
        """
        logger.info(f"Loading and reconstructing conversations for {self.brand_id}...")

        # 1. First pass: Build parent map and identify relevant tweet IDs without loading full text
        cols_for_map = ['tweet_id', 'in_response_to_tweet_id', 'author_id']
        parent_map = {}
        relevant_ids = set()

        chunk_size = 100_000
        for chunk in pd.read_csv(file_path, usecols=cols_for_map, chunksize=chunk_size):
            # Populate parent map
            # Use zip to avoid DataFrame overhead for this map
            for tid, parent in zip(chunk['tweet_id'], chunk['in_response_to_tweet_id']):
                parent_map[tid] = parent

            # Identify relevant tweets (by brand or responded to by brand)
            # To do this accurately, we need the full brand_tweet_ids first.
            # Let's collect all brand tweet IDs in this pass.
            brand_tweets_in_chunk = chunk[chunk['author_id'] == self.brand_id]['tweet_id'].tolist()
            relevant_ids.update(brand_tweets_in_chunk)

        # Now we have all brand tweet IDs, we can find all tweets they responded to
        # (This is a bit inefficient but memory safe)
        # Actually, let's refine: a tweet is relevant if:
        # a) author_id == brand_id
        # b) tweet_id in {all brand tweets' in_response_to_tweet_id}

        # Let's do it more cleanly.
        # We'll re-read the file in chunks to build the final filtered set.
        # But first, let's refine relevant_ids.
        # We need the IDs of tweets that the brand responded to.
        brand_responded_to = set()
        for chunk in pd.read_csv(file_path, usecols=cols_for_map, chunksize=chunk_size):
            brand_tweets = chunk[chunk['author_id'] == self.brand_id]
            brand_responded_to.update(brand_tweets['in_response_to_tweet_id'].dropna().tolist())

        relevant_ids.update(brand_responded_to)

        # Second pass: Load only the relevant tweets' full data
        relevant_data = []
        cols_to_load = ['tweet_id', 'author_id', 'inbound', 'created_at', 'text', 'in_response_to_tweet_id']
        for chunk in pd.read_csv(file_path, usecols=cols_to_load, chunksize=chunk_size):
            filtered_chunk = chunk[chunk['tweet_id'].isin(relevant_ids)].copy()
            relevant_data.append(filtered_chunk)

        df_filtered = pd.concat(relevant_data)

        # Now run the reconstruction logic on the much smaller filtered set
        return self._reconstruct_from_filtered(df_filtered, parent_map)

    def _reconstruct_from_filtered(self, df_filtered: pd.DataFrame, parent_map: dict) -> pd.DataFrame:
        # Normalize Schema
        all_ids = set(parent_map.keys())
        conversation_map = {}

        def find_root(tid):
            path = []
            curr = tid
            while True:
                if curr in conversation_map:
                    root = conversation_map[curr]
                    break
                parent = parent_map.get(curr)
                if pd.isna(parent) or parent not in all_ids:
                    root = curr
                    break
                path.append(curr)
                curr = parent
            for p in path:
                conversation_map[p] = root
            return root

        logger.info("Assigning conversation IDs...")
        df_filtered['conversation_id'] = df_filtered['tweet_id'].apply(find_root)

        # Determine author_type
        df_filtered['author_type'] = df_filtered['inbound'].map({True: 'CUSTOMER', False: 'BRAND'})

        # Normalizing text
        logger.info("Cleaning text...")
        cleaned_texts = df_filtered['text'].apply(self.cleaner.clean)
        df_filtered['normalized_text'] = [x[0] for x in cleaned_texts]
        df_filtered['raw_text'] = [x[1] for x in cleaned_texts]

        # Conversation position
        df_filtered['created_at'] = pd.to_datetime(df_filtered['created_at'])
        df_filtered = df_filtered.sort_values(['conversation_id', 'created_at'])
        df_filtered['conversation_position'] = df_filtered.groupby('conversation_id').cumcount()

        final_cols = [
            'conversation_id', 'tweet_id', 'in_response_to_tweet_id',
            'created_at', 'author_type', 'author_id',
            'normalized_text', 'raw_text', 'conversation_position'
        ]
        return df_filtered[final_cols]

    def create_interaction_dataset(self, normalized_df: pd.DataFrame) -> pd.DataFrame:
        """
        Creates a cleaned interaction dataset:
        (customer_message, conversation_context, historical_brand_response, metadata)
        """
        logger.info("Creating interaction dataset (Pairs)...")
        interactions = []

        for conv_id, group in normalized_df.groupby('conversation_id'):
            # A usable interaction is a CUSTOMER message followed by a BRAND response
            group = group.sort_values('conversation_position')

            for i in range(len(group) - 1):
                curr = group.iloc[i]
                nxt = group.iloc[i+1]

                if curr['author_type'] == 'CUSTOMER' and nxt['author_type'] == 'BRAND':
                    # Found a pair!
                    # Context is all messages before the customer message in this conversation
                    context = " ".join(group.iloc[:i]['normalized_text'].tolist())

                    interactions.append({
                        "conversation_id": conv_id,
                        "customer_message": curr['normalized_text'],
                        "customer_raw": curr['raw_text'],
                        "conversation_context": context,
                        "historical_brand_response": nxt['normalized_text'],
                        "brand_raw": nxt['raw_text'],
                        "metadata": {
                            "customer_tweet_id": curr['tweet_id'],
                            "brand_tweet_id": nxt['tweet_id'],
                            "position": curr['conversation_position']
                        }
                    })

        return pd.DataFrame(interactions)
