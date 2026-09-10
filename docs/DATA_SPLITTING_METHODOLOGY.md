# Data Splitting Methodology

**Brand:** AmazonHelp

## Leakage Prevention
To prevent data leakage, the dataset was split at the **conversation level**.
This ensures that if a conversation has multiple interactions, all of them
fall into the same split (Train, Val, or Test). A random shuffle of unique
conversation IDs was performed with a fixed seed (42) for reproducibility.

## Split Ratios
- Train: 80%
- Validation: 10%
- Test: 10%

## Metrics
- Total Unique Conversations: 1680
- Train Set Size: 1350 pairs
- Val Set Size: 169 pairs
- Test Set Size: 169 pairs
