import streamlit as st
import os
from datetime import datetime
import json
import time
import pandas as pd

from utils.pdf import extract_text_from_pdf
from utils.ai import get_ai_feedback, parse_scores_enhanced, extract_enhanced_feedback
from utils.visuals import create_enhanced_radar_chart, create_score_history_chart
from utils.helpers import get_score_color_class, calculate_weighted_score, get_file_hash

# === Page Config ===
st.set_page_config(page_title="ScoreScope AI", layout="wide", initial_sidebar_state="expanded")

# === CSS Styling ===
with open("scorescope_custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === Default Categories ===
DEFAULT_CATEGORIES = {
    "Requirements Fulfillment": 25,
    "Content Quality & Depth": 20,
    "Clarity & Communication": 18,
    "Structure & Organization": 15,
    "Critical Thinking": 12,
    "Presentation & Format": 10
}

# === Header ===
st.markdown("""
<div class="main-header">
    <h1>ScoreScope<span style="font-size: 0.6em; vertical-align: super; font-weight: normal;">ai</span></h1>
    <p>Upload your work and get comprehensive, AI-powered evaluation with actionable insights</p>
</div>
""", unsafe_allow_html=True)

# === Sidebar Configuration ===
with st.sidebar:
    st.header("Configuration")
    eval_style = st.selectbox("Evaluation Style", ["balanced", "strict", "encouraging"])
    if st.checkbox("Customize Categories"):
        st.subheader("Edit Evaluation Categories")
        categories = {}
        for i, (cat, weight) in enumerate(DEFAULT_CATEGORIES.items()):
            col1, col2 = st.columns([3, 1])
            with col1:
                cat_name = st.text_input(f"Category {i+1}", value=cat, key=f"cat_{i}")
            with col2:
                cat_weight = st.number_input("Weight", value=weight, min_value=1, max_value=50, key=f"weight_{i}")
            if cat_name:
                categories[cat_name] = cat_weight
        if sum(categories.values()) != 100:
            st.warning("Weights must sum to 100%")
    else:
        categories = DEFAULT_CATEGORIES

    with st.expander("Advanced Settings"):
        max_pages = st.slider("Max pages to analyze", 5, 30, 15)
        show_raw_response = st.checkbox("Show raw AI response")

# === Upload & Task Input ===
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Task Instructions")
    task_outline = st.text_area("Describe what you were asked to do:", height=200)

with col2:
    st.subheader("Upload Your Work")
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Drop your PDF here", type=["pdf"])
    st.markdown('</div>', unsafe_allow_html=True)
    if uploaded_pdf:
        st.success(f"Uploaded: {uploaded_pdf.name}")

# === Analyze Button ===
if st.button("Analyze with ScoreScope AI"):
    if not uploaded_pdf or not task_outline.strip():
        st.error("Please upload a PDF and enter task instructions.")
    else:
        start_time = time.time()
        file_hash = get_file_hash(uploaded_pdf)

        st.info("Processing your submission...")
        submission_text = extract_text_from_pdf(file_hash, uploaded_pdf, max_pages)
        if not submission_text:
            st.stop()

        ai_response = get_ai_feedback(task_outline, submission_text, categories, eval_style)
        if ai_response.startswith("ERROR"):
            st.error(ai_response)
            st.stop()

        scores = parse_scores_enhanced(ai_response, categories)
        feedback_data = extract_enhanced_feedback(ai_response)
        weighted_score = calculate_weighted_score(scores, categories)

        st.header("Evaluation Results")
        score_class = get_score_color_class(weighted_score)
        st.markdown(f"""
        <div class="metric-container {score_class}">
            <h2 style="
                text-align: center;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                color: transparent;
                margin: 0;
            ">Overall Score</h2>
            <h1 style="text-align: center; margin: 0;">{weighted_score}/10</h1>
            <p style="text-align: center; margin: 0; opacity: 0.7;">Processed in {time.time() - start_time:.1f}s</p>
        </div>
        """, unsafe_allow_html=True)

        st.plotly_chart(create_enhanced_radar_chart(scores), use_container_width=True)

        st.subheader("Detailed Category Analysis")
        for category, (score, explanation) in scores.items():
            with st.expander(f"{category}: {score}/10"):
                st.markdown(f"**Weight:** {categories[category]}%")
                st.markdown(f"**Analysis:** {explanation}")

        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.subheader("Overall Assessment")
        st.write(feedback_data["overall"])
        st.subheader("Action Plan")
        for i, action in enumerate(feedback_data["actions"], 1):
            st.markdown(f"**{i}.** {action}")
        st.markdown('</div>', unsafe_allow_html=True)

        # === History ===
        if "evaluation_history" not in st.session_state:
            st.session_state.evaluation_history = []
        st.session_state.evaluation_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "overall_score": weighted_score,
            **{cat: score for cat, (score, _) in scores.items()}
        })

        if len(st.session_state.evaluation_history) > 1:
            st.subheader("Your Progress")
            st.plotly_chart(create_score_history_chart(st.session_state.evaluation_history), use_container_width=True)
            df_history = pd.DataFrame(st.session_state.evaluation_history)
            st.dataframe(df_history, use_container_width=True)

        # === Export ===
        with st.expander("Export Results"):
            col1, col2 = st.columns(2)
            with col1:
                export_data = {
                    "task": task_outline,
                    "scores": {cat: score for cat, (score, _) in scores.items()},
                    "weighted_score": weighted_score,
                    "feedback": feedback_data,
                    "timestamp": datetime.now().isoformat()
                }
                st.download_button("Download (JSON)", data=json.dumps(export_data, indent=2),
                                   file_name="scorescope_results.json", mime="application/json")
            with col2:
                report = f"""EVALUATION REPORT\n\nOverall Score: {weighted_score}/10\n\nCATEGORY SCORES:\n""" + \
                         "\n".join([f"- {cat}: {score}/10" for cat, (score, _) in scores.items()]) + \
                         f"\n\nASSESSMENT:\n{feedback_data['overall']}\n\nACTION PLAN:\n" + \
                         "\n".join([f"{i}. {a}" for i, a in enumerate(feedback_data['actions'], 1)])
                st.download_button("Download (TXT)", data=report,
                                   file_name="scorescope_report.txt", mime="text/plain")

        if show_raw_response:
            with st.expander("Raw AI Response"):
                st.text(ai_response)
