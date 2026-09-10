# Dataset Verification Report

## Dataset Source
- **Expected**: `thoughtvector/customer-support-on-twitter`
- **Verified**: Raw data found in `data/twcs.csv`.
- **Row Count**: 3,002,524 (matches expectation).

## Brand Verification
- **Reported Brand**: `AmazonHelp`
- **Verified**: `grep` confirmed presence of `AmazonHelp` in the dataset.
- **Observation**: The dataset contains multiple brands (e.g., `sprintcare`, `Ask_Spectrum`). The system is designed to filter for a specific brand.

## Data Structure
- **Columns**: `tweet_id`, `author_id`, `inbound`, `created_at`, `text`, `response_tweet_id`, `in_response_to_tweet_id`.
- **Format**: CSV.
- **Integrity**: Rows appear well-formed, though some text contains emojis and non-English characters (e.g., Japanese), which the system must handle.

## Conclusion
The dataset is genuine and contains the reported brand.
