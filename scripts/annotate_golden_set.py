import os

import pandas as pd
import streamlit as st

# Configuration
DATA_PATH = "data/processed/train.csv"
GOLDEN_SET_PATH = "evaluation/golden_set.csv"
METADATA_PATH = "evaluation/golden_set_metadata.json"

st.set_page_config(page_title="Golden Set Annotator", layout="wide")

st.title("Golden Set Annotator")
st.markdown("Label training examples to create the frozen evaluation set.")

# Load data
@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        return None
    return pd.read_csv(DATA_PATH)

df = load_data()

if df is None:
    st.error(f"Data not found at {DATA_PATH}. Please run `scripts/prepare_data.py` first.")
    st.stop()

# Load existing labels
if os.path.exists(GOLDEN_SET_PATH):
    golden_set = pd.read_csv(GOLDEN_SET_PATH)
    labeled_ids = set(golden_set['customer_message'].tolist()) # Using message as ID for simplicity here, should use tweet_id
else:
    golden_set = pd.DataFrame()
    labeled_ids = set()

# Intents from taxonomy
INTENTS = [
    "Delivery & Shipping",
    "Refunds & Returns",
    "Account & Security",
    "Order Status & Tracking",
    "Payment & Billing",
    "Product Quality & Warranty",
    "Customer Service Access",
    "Severe Complaint / Fraud"
]

# Sampling a batch of unlabeled examples
unlabeled_df = df[~df['customer_message'].isin(labeled_ids)]
if unlabeled_df.empty:
    st.success("All examples labeled!")
    st.stop()

# Session state for current example
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0

current_example = unlabeled_df.iloc[st.session_state.current_idx]

st.divider()

# UI Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Example")
    st.text_area("Customer Message", value=current_example['customer_message'], height=100, disabled=True)
    st.text_area("Conversation Context", value=current_example['conversation_context'], height=100, disabled=True)
    st.info(f"Example {st.session_state.current_idx + 1} of {len(unlabeled_df)}")

with col2:
    st.subheader("Labels")
    intent = st.selectbox("Intent", options=INTENTS)
    should_escalate = st.radio("Should Escalate?", options=["No", "Yes"])
    escalation_reason = st.text_input("Escalation Reason (if Yes)")
    confidence = st.slider("Annotation Confidence", 0.0, 1.0, 1.0, 0.1)
    notes = st.text_area("Notes")

    if st.button("Save Label", type="primary"):
        new_label = pd.DataFrame([{
            "customer_message": current_example['customer_message'],
            "conversation_context": current_example['conversation_context'],
            "gold_intent": intent,
            "should_escalate": "Yes" if should_escalate == "Yes" else "No",
            "escalation_reason": escalation_reason,
            "annotation_confidence": confidence,
            "annotator_notes": notes
        }])

        # Append to golden set
        golden_set = pd.concat([golden_set, new_label], ignore_index=True)
        golden_set.to_csv(GOLDEN_SET_PATH, index=False)

        st.session_state.current_idx += 1
        st.rerun()

st.divider()
st.write(f"Progress: {len(labeled_ids)} / {len(df)}")
if not golden_set.empty:
    st.download_button("Download Golden Set CSV", golden_set.to_csv(index=False), "golden_set.csv", "text/csv")
