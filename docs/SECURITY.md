# Security and Safety Documentation

This document outlines the security measures and safety guardrails implemented in the Hiver AI Support Agent prototype.

## 1. Secret Management
The system is designed to ensure that no sensitive credentials are committed to version control.
-   **Environment Variables**: All API keys (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`) must be stored in a `.env` file or system environment variables.
-   **Local Config**: `config/config.yaml` contains non-sensitive operational parameters (taxonomy, thresholds).
-   **Git Hygiene**: A strict `.gitignore` is in place to block `.env` and other secret-bearing files.

## 2. PII Handling and Data Safety
To prevent the leakage of Personally Identifiable Information (PII), the system implements several layers of protection:
-   **Normalization**: The `TextCleaner` replaces usernames and URLs with generic tokens (`[USER]`, `[URL]`) during preprocessing.
-   **Safety Guard**: The generation pipeline includes a safety check to detect and block responses containing potential PII (e.g., order IDs, email addresses) before they reach the user.

## 3. Prompt Injection and Input Validation
The system manages the risk of prompt injection (adversarial inputs designed to hijack the LLM) through:
-   **Structured Prompting**: Using clear delimiters between system instructions, retrieved evidence, and user input.
-   **Input Sanitization**: Basic cleaning of excessive punctuation and special characters in the `TextCleaner` class.
-   **Output Validation**: Using Pydantic to enforce strict JSON schemas for all LLM outputs, preventing the system from executing malformed or unexpected instructions.

## 4. LLM Failure and Reliability
To ensure system stability during API failures:
-   **Bounded Retries**: The `LLMClient` implements exponential backoff for 429 (Rate Limit) and 500 (Server Error) responses.
-   **Safe Fallbacks**: If the LLM fails to return a valid response, the system falls back to a safe, generic response: *"I'm sorry, I'm having trouble processing your request. Please hold on while I connect you to a specialist."*
-   **Fallback Retrieval**: If the embedding model fails, the system reverts to a deterministic keyword-overlap search.

## 5. Generated Response Safety
All generated responses are audited via the `EscalationSystem` and `SafetyGuard`:
-   **PII Leakage**: Responses are scanned for leaked IDs.
-   **Hallucinated Data**: The Claim-Support Verification pipeline identifies and marks unsupported factual claims.
-   **Toxicity/Tone**: The LLM Judge scores responses on a "Safety" dimension to ensure they remain professional and non-harmful.
