# Intent Taxonomy Audit

## Taxonomy Review
- **Documented Intents**: 8 distinct categories (Delivery & Shipping, Refunds & Returns, Account & Security, Order Status & Tracking, Payment & Billing, Product Quality & Warranty, Customer Service Access, Severe Complaint / Fraud).
- **Definitions**: Clear and well-separated. Inclusion/Exclusion criteria are provided.
- **Consistency**: The taxonomy is logically sound and covers the main support surface.

## Implementation Discrepancy
- **Finding**: The `AIIntentClassifier` in `src/intent/ai_classifier.py` implements a mapping that collapses the 8 documented intents into a smaller set.
- **Mapping Logic**:
    - `Delivery & Shipping` $\rightarrow$ `Order & Logistics`
    - `Order Status & Tracking` $\rightarrow$ `Order & Logistics`
    - `Refunds & Returns` $\rightarrow$ `Order & Logistics`
    - `Customer Service Access` $\rightarrow$ `General Inquiry`
    - `Severe Complaint / Fraud` $\rightarrow$ `General Inquiry`
    - `Account & Security` $\rightarrow$ `Account Access`
    - `Payment & Billing` $\rightarrow$ `Billing & Subscriptions`
    - `Product Quality & Warranty` $\rightarrow$ `Warranty & Repairs`
- **Impact**: The implementation does not match the documented taxonomy. This leads to lower granularity in classification and potential confusion during evaluation if the golden set uses the 8-intent version but the system reports the collapsed version.

## Conclusion
The documentation and implementation are out of sync. The system is effectively using a 5-6 intent taxonomy while documenting 8.
