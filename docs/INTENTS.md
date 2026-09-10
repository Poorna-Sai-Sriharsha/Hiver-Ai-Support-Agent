# Intent Taxonomy: AmazonHelp

This taxonomy is derived from an analysis of historical customer interactions for AmazonHelp using TF-IDF clustering and manual review of representative examples.

## Defined Intents

### 1. Delivery & Shipping
- **Definition**: Inquiries or complaints regarding the transport and delivery of an order.
- **Inclusion Criteria**: Mentions of shipping speed, delivery dates, "two-day shipping", courier issues, or delayed arrival.
- **Exclusion Criteria**: General product quality issues or refund requests.
- **Example**: "[USER] if something is \"free two day shipping\" with prime, why is it taking four days?"

### 2. Refunds & Returns
- **Definition**: Requests for money back or questions about returning a product.
- **Inclusion Criteria**: Explicit requests for "refund", "money back", "return a product", or issues with the return process.
- **Exclusion Criteria**: Simple delivery delays without a request for a refund.
- **Example**: "[USER] Need to get a refund of this product that I returned."

### 3. Account & Security
- **Definition**: Issues accessing the account or security-related concerns.
- **Inclusion Criteria**: Mentions of "login", "password", "account locked", "account reinstatement", or "security".
- **Exclusion Criteria**: General questions about how to use the website.
- **Example**: "[USER] Please help in reinstate my account"

### 4. Order Status & Tracking
- **Definition**: Requests for information on where an order is currently located.
- **Inclusion Criteria**: Questions about "where is my order", "tracking number", "order status", or "did it ship".
- **Exclusion Criteria**: Complaints about the delivery being late (that goes to Delivery & Shipping).
- **Example**: "[USER] Where is my order #12345?"

### 5. Payment & Billing
- **Definition**: Issues related to charges, payments, and subscriptions.
- **Inclusion Criteria**: Mentions of "charge", "billing error", "Prime subscription", "credit card", or "invoice".
- **Exclusion Criteria**: Refund requests (that goes to Refunds & Returns).
- **Example**: "Signed up for a free Amazon Prime trial and now they're trying to charge my card the £79 anyway?"

### 6. Product Quality & Warranty
- **Definition**: Complaints about the physical state or functionality of a received product.
- **Inclusion Criteria**: Mentions of "damaged", "broken", "warranty", "defective", or "not as described".
- **Exclusion Criteria**: Delivery damage (that goes to Delivery & Shipping).
- **Example**: "[USER] Bonjour, L'article est totalement endommagé"

### 7. Customer Service Access
- **Definition**: Difficulty in contacting Amazon support or complaints about the support experience.
- **Inclusion Criteria**: Questions about "how to contact", "customer care", "dropped calls", or "reach you fast".
- **Exclusion Criteria**: Specific issues with an order (those should be categorized by the issue type).
- **Example**: "[USER] trying to call the customer support without any luck. What's the best way to reach you fast?"

### 8. Severe Complaint / Fraud
- **Definition**: High-severity interactions involving accusations of fraud, legal threats, or extreme anger.
- **Inclusion Criteria**: Use of words like "fraud", "cheat", "court", "liars", or extremely aggressive tone.
- **Exclusion Criteria**: Standard complaints about late delivery.
- **Example**: "[USER] #fraudamazon #cheat #dontbuy Order id:406-1634211-8172338"

## Common Confusions
- **Delivery vs. Order Status**: "Where is my order?" (Status) vs "Why is my order late?" (Delivery).
- **Refund vs. Billing**: "I was charged twice" (Billing) vs "I want my money back for this broken item" (Refund).
- **Product Quality vs. Delivery**: "The box arrived crushed" (Delivery) vs "The item inside is broken" (Product Quality).
