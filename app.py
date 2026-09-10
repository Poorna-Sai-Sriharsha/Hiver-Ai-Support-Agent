import json
import os

import numpy as np
import pandas as pd
import streamlit as st

from src.agent import SupportAgent
from src.retrieval.vector_store import VectorStore
from src.utils.llm_client import LLMClient

st.set_page_config(page_title="Hiver AI Support Ops", layout="wide")

# --- State & Cache ---
@st.cache_resource
def load_agent():
    # Load config and data
    with open("config/config.yaml", 'r') as f:
        import yaml
        yaml.safe_load(f)

    kb = VectorStore()
    # Index from processed train data
    if os.path.exists("data/processed/train.csv"):
        train_df = pd.read_csv("data/processed/train.csv")
        kb.index_data(train_df)

    return SupportAgent("config/config.yaml", kb, LLMClient())

agent = load_agent()

# --- Sidebar Navigation ---
st.sidebar.title("Support Operations")
page = st.sidebar.radio("Navigation", [
    "Overview",
    "Live Support Agent",
    "Evaluation Dashboard",
    "Failure Analysis",
    "Golden Set",
    "Golden Set Annotator",
    "Human Judge",
    "Decision Log"
])

# --- Page: Overview ---
if page == "Overview":
    st.title("System Overview")

    # Load real metrics if available
    metrics_data = {}
    if os.path.exists("artifacts/metrics.json"):
        with open("artifacts/metrics.json", "r") as f:
            metrics_data = json.load(f)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Selected Brand", "AmazonHelp")
    with col2:
        # Use real Macro-F1 if available
        macro_f1 = metrics_data.get('ai', {}).get('intent', {}).get('macro_f1', "N/A")
        st.metric("Headline Metric", f"{macro_f1:.4f}" if isinstance(macro_f1, float) else macro_f1, "Macro-F1")
    with col3:
        # Dynamic Golden Set Size
        gs_size = 0
        if os.path.exists("evaluation/annotation_queue.csv"):
            gs_size = len(pd.read_csv("evaluation/annotation_queue.csv"))
        st.metric("Golden Set Size", str(gs_size))
    with col4:
        st.metric("System Version", "v1.0.0-beta")

    st.divider()
    st.subheader("Dataset Statistics")
    # Load data stats from profile
    if os.path.exists("data_profile.json"):
        with open("data_profile.json", "r") as f:
            profile = json.load(f)

        c1, c2, c3 = st.columns(3)
        c1.write(f"**Total Rows:** {profile['basic_stats']['row_count']}")
        c2.write(f"**Total Brands:** {profile['brand_stats']['total_brands']}")
        c3.write(f"**Customer Tweets:** {profile['tweet_types']['customer_tweets']}")

# --- Page: Live Support Agent ---
elif page == "Live Support Agent":
    st.title("Live Support Agent")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Input")
        customer_msg = st.text_area("Customer Message", placeholder="Enter customer query here...", height=150)
        context = st.text_area("Conversation Context (Optional)", placeholder="Previous messages...", height=100)

        if st.button("Process Message", type="primary"):
            if customer_msg:
                res = agent.process_message(customer_msg, context)
                st.session_state['last_res'] = res
            else:
                st.warning("Please enter a message.")

    with col2:
        st.subheader("Agent Analysis")
        if 'last_res' in st.session_state:
            res = st.session_state['last_res']

            # Intent
            st.markdown(f"**Intent:** `{res['intent']}` (Confidence: {res['intent_confidence']:.2f})")

            # Escalation
            esc = res['escalation']
            color = "red" if esc['decision'] == "ESCALATED" else "green"
            st.markdown(f"**Decision:** :{color}[{esc['decision']}]")
            st.markdown(f"**Reason:** {esc['reason']}")

            st.divider()
            st.markdown("**Draft Reply:**")
            st.info(res['reply'])

            st.divider()
            st.markdown("**Historical Evidence**")
            for i, ev in enumerate(res['evidence']):
                with st.expander(f"Evidence {i+1} (Score: {ev['score']:.2f})"):
                    st.markdown(f"**Customer:** {ev['customer_message']}")
                    st.markdown(f"**Brand Response:** {ev['brand_response']}")

# --- Page: Evaluation Dashboard ---
elif page == "Evaluation Dashboard":
    st.title("Evaluation Dashboard")

    if os.path.exists("artifacts/metrics.json"):
        with open("artifacts/metrics.json", "r") as f:
            metrics = json.load(f)

        st.subheader("Intent Performance")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Comparison across baselines")
            # Create a simple DF for plotting
            comp_df = pd.DataFrame({
                "Baseline": ["Trivial", "Simple", "AI Agent"],
                "Accuracy": [
                    metrics.get('trivial', {}).get('accuracy', 0),
                    metrics.get('simple', {}).get('accuracy', 0),
                    metrics.get('ai', {}).get('accuracy', 0)
                ],
                "Macro-F1": [
                    metrics.get('trivial', {}).get('macro_f1', 0),
                    metrics.get('simple', {}).get('macro_f1', 0),
                    metrics.get('ai', {}).get('macro_f1', 0)
                ]
            })
            st.bar_chart(comp_df, x="Baseline", y="Accuracy")

        with col2:
            st.write("Escalation Metrics")
            # Use real False Auto-Handle Rate if available
            false_auto_rate = metrics_data.get('ai', {}).get('escalation', {}).get('false_auto_handle_rate', "N/A")
            st.metric("False Auto-Handle Rate", f"{false_auto_rate:.2%}" if isinstance(false_auto_rate, float) else false_auto_rate)

# --- Page: Failure Analysis ---
elif page == "Failure Analysis":
    st.title("Failure Analysis")
    if os.path.exists("artifacts/failure_analysis.json"):
        with open("artifacts/failure_analysis.json", "r") as f:
            failures = json.load(f)

        for i, fail in enumerate(failures):
            with st.container():
                st.subheader(f"Failure Mode {i+1}: {fail['mode']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Example:** {fail['example']}")
                    st.markdown(f"**Expected:** {fail['expected']}")
                with col2:
                    st.markdown(f"**Actual:** {fail['actual']}")
                    st.markdown(f"**Diagnosis:** {fail['diagnosis']}")
                st.divider()
    else:
        st.info("No failure analysis artifacts found. Run the evaluation pipeline first.")

# --- Page: Golden Set ---
elif page == "Golden Set":
    st.title("Golden Set Review")
    if os.path.exists("evaluation/golden_set.csv"):
        gs = pd.read_csv("evaluation/golden_set.csv")
        st.dataframe(gs, use_container_width=True)
    else:
        st.warning("Golden set not found.")

# --- Page: Decision Log ---
elif page == "Decision Log":
    st.title("Engineering Decision Log")
    if os.path.exists("DECISION_LOG.md"):
        with open("DECISION_LOG.md", "r") as f:
            st.markdown(f.read())
    else:
        st.info("Decision log not yet created.")


# --- Page: Human Judge ---
elif page == "Human Judge":
    st.title("Human Judge Validation")

    # We need a set of results to judge
    results_path = "artifacts/evaluation_results.json"
    if not os.path.exists(results_path):
        st.warning("No evaluation results found. Please run the evaluation pipeline first.")
        st.stop()

    with open(results_path, "r") as f:
        results = json.load(f)

    # Sampling for human judge (40-60 samples)
    np.random.seed(42)
    if len(results) > 60:
        judge_sample_indices = np.random.choice(len(results), 60, replace=False)
    else:
        judge_sample_indices = range(len(results))

    # Load current human scores
    scores_path = "evaluation/human_scores.csv"
    if os.path.exists(scores_path):
        scores_df = pd.read_csv(scores_path)
    else:
        scores_df = pd.DataFrame(columns=['example_id', 'relevance', 'correctness', 'groundedness', 'helpfulness', 'tone', 'safety', 'completeness', 'timestamp'])

    # Select example to judge
    # Find unjudged examples
    judged_ids = set(scores_df['example_id'].astype(str).unique()) if not scores_df.empty else set()
    unjudged_indices = [i for i in judge_sample_indices if str(i) not in judged_ids]

    if not unjudged_indices:
        st.success("All sample responses judged!")
    else:
        st.subheader(f"Progress: {len(judged_ids)} / {len(judge_sample_indices)}")
        idx = st.selectbox("Select Example to Score", unjudged_indices)
        res = results[idx]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Context")
            st.info(f"Customer: {res['original_message']}")
            st.markdown("### Agent Response")
            st.success(res['reply'])
            st.markdown("### Evidence Used")
            for i, ev in enumerate(res['evidence']):
                st.write(f"**{i+1}.** {ev['brand_response']}")

        with col2:
            st.markdown("### 📊 Scoring (0-4)")
            rel = st.slider("Relevance", 0, 4, 3)
            cor = st.slider("Correctness", 0, 4, 3)
            gro = st.slider("Groundedness", 0, 4, 3)
            hel = st.slider("Helpfulness", 0, 4, 3)
            ton = st.slider("Tone", 0, 4, 3)
            saf = st.slider("Safety", 0, 4, 4)
            com = st.slider("Completeness", 0, 4, 3)

            if st.button("Save Score", type="primary"):
                new_score = pd.DataFrame([{
                    'example_id': str(idx),
                    'relevance': rel,
                    'correctness': cor,
                    'groundedness': gro,
                    'helpfulness': hel,
                    'tone': ton,
                    'safety': saf,
                    'completeness': com,
                    'timestamp': pd.Timestamp.now().isoformat()
                }])
                scores_df = pd.concat([scores_df, new_score], ignore_index=True)
                scores_df.to_csv(scores_path, index=False)
                st.success("Score saved!")
                st.rerun()

# --- Page: Golden Set Annotator ---
elif page == "Golden Set Annotator":
    st.title("Human Golden Set Annotator")

    # Load Taxonomy
    try:
        with open("config/intents.yaml", "r") as f:
            import yaml
            taxonomy = yaml.safe_load(f)['intents']
            intent_names = [i['name'] for i in taxonomy]
    except (yaml.YAMLError, KeyError, FileNotFoundError) as e:
        st.error(f"Could not load taxonomy: {e}")
        st.stop()

    queue_path = "evaluation/annotation_queue.csv"
    if not os.path.exists(queue_path):
        st.warning("No annotation queue found. Please run `python scripts/sample_for_annotation.py` first.")
        st.stop()

    df = pd.read_csv(queue_path)
    unannotated = df[df['is_annotated'] == False]

    if unannotated.empty:
        st.success("All examples annotated!")
    else:
        st.subheader(f"Progress: {len(df) - len(unannotated)} / {len(df)}")

        # Select example to annotate
        idx = st.selectbox("Select Example Index", unannotated.index)
        row = df.loc[idx]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### Customer Message")
            st.info(row['customer_message'])
            st.markdown("### Brand Response (Reference)")
            st.success(row['historical_brand_response'])

        with col2:
            st.markdown("### Annotation")

            # Intent
            gold_intent = st.selectbox("Correct Intent", options=intent_names)

            # Escalation
            should_escalate = st.radio("Should this be escalated?", options=["No", "Yes"])
            esc_reason = st.text_input("Escalation Reason (if Yes)")

            # Severity
            severity = st.select_slider("Severity", options=["Low", "Medium", "High", "Critical"])

            # Expected Response
            expected_points = st.text_area("Expected Response Characteristics", placeholder="What MUST be in the reply?")

            # Meta
            confidence = st.slider("Annotation Confidence", 0.0, 1.0, 1.0, 0.1)
            notes = st.text_input("Notes")

            if st.button("Save Annotation", type="primary"):
                df.at[idx, 'gold_intent'] = gold_intent
                df.at[idx, 'should_escalate'] = should_escalate
                df.at[idx, 'escalation_reason'] = esc_reason
                df.at[idx, 'severity'] = severity
                df.at[idx, 'expected_response_points'] = expected_points
                df.at[idx, 'annotation_confidence'] = confidence
                df.at[idx, 'annotator_notes'] = notes
                df.at[idx, 'is_annotated'] = True
                df.at[idx, 'annotation_timestamp'] = pd.Timestamp.now().isoformat()

                df.to_csv(queue_path, index=False)
                st.success("Annotation saved!")
                st.rerun()
