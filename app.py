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

# Page Config - Must be first
st.set_page_config(
    page_title="ScoreScope AI - Portfolio Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with portfolio-grade styling
def load_enhanced_css():
    st.markdown("""
    <style>
    /* Hide Streamlit branding completely */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display: none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    
    /* Import Figtree font */
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap');
    
    /* Global app styling */
    .stApp {
        background: #000000;
        font-family: 'Figtree', sans-serif;
        color: #ffffff;
    }
    
    /* Custom header section */
    .header-container {
        background: rgba(20, 20, 20, 0.95);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(129, 74, 200, 0.2);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 32px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #814AC8, transparent);
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        margin-bottom: 16px;
    }
    
    .logo-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #814AC8 0%, #5B4FC7 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 8px 32px rgba(129, 74, 200, 0.3);
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.8) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.7);
        margin: 8px 0 0 0;
        font-weight: 400;
    }
    
    /* Main content cards */
    .content-card {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid rgba(129, 74, 200, 0.3);
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .content-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(129, 74, 200, 0.5), transparent);
    }
    
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .section-icon {
        width: 32px;
        height: 32px;
        background: rgba(129, 74, 200, 0.2);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    
    /* Enhanced input styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(129, 74, 200, 0.4) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-family: 'Figtree', sans-serif !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        padding: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #814AC8 !important;
        box-shadow: 0 0 0 3px rgba(129, 74, 200, 0.2) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Enhanced file uploader */
    .stFileUploader > div {
        background: rgba(129, 74, 200, 0.08) !important;
        border: 2px dashed rgba(129, 74, 200, 0.4) !important;
        border-radius: 16px !important;
        padding: 32px !important;
        text-align: center !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover > div {
        border-color: #814AC8 !important;
        background: rgba(129, 74, 200, 0.12) !important;
        transform: translateY(-2px) !important;
    }
    
    .stFileUploader label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }
    
    /* Premium button styling */
    .stButton > button {
        background: linear-gradient(135deg, #814AC8 0%, #5B4FC7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        font-family: 'Figtree', sans-serif !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 32px rgba(129, 74, 200, 0.3) !important;
        width: 100% !important;
        height: 56px !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 40px rgba(129, 74, 200, 0.4) !important;
        background: linear-gradient(135deg, #9557e5 0%, #6f4fc7 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Results styling */
    .results-container {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid rgba(129, 74, 200, 0.3);
        border-radius: 20px;
        padding: 40px;
        margin: 24px 0;
        backdrop-filter: blur(20px);
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.4);
    }
    
    .score-display {
        text-align: center;
        padding: 32px;
        background: rgba(129, 74, 200, 0.1);
        border-radius: 20px;
        border: 1px solid rgba(129, 74, 200, 0.3);
        margin: 24px 0;
        position: relative;
        overflow: hidden;
    }
    
    .score-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #814AC8, #A855F7, #814AC8);
    }
    
    .overall-score {
        font-size: 64px;
        font-weight: 800;
        background: linear-gradient(135deg, #814AC8 0%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1;
        letter-spacing: -2px;
    }
    
    .score-label {
        font-size: 16px;
        color: rgba(255, 255, 255, 0.6);
        margin-top: 12px;
        font-weight: 500;
    }
    
    /* Category analysis styling */
    .category-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(129, 74, 200, 0.2);
        border-left: 4px solid #814AC8;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }
    
    .category-container:hover {
        background: rgba(255, 255, 255, 0.05);
        border-left-width: 6px;
        transform: translateX(4px);
    }
    
    .category-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .category-name {
        font-size: 18px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.9);
    }
    
    .category-score {
        font-size: 20px;
        font-weight: 700;
        color: #814AC8;
        background: rgba(129, 74, 200, 0.1);
        padding: 4px 12px;
        border-radius: 8px;
    }
    
    .category-weight {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 8px;
    }
    
    /* Processing animation */
    .processing-container {
        text-align: center;
        padding: 40px;
        background: rgba(129, 74, 200, 0.05);
        border-radius: 16px;
        border: 1px solid rgba(129, 74, 200, 0.2);
        margin: 24px 0;
    }
    
    .processing-text {
        font-size: 18px;
        color: #814AC8;
        font-weight: 600;
        margin-bottom: 16px;
        animation: pulse 2s infinite;
    }
    
    /* Progress bar enhancement */
    .stProgress > div > div {
        background: linear-gradient(90deg, #814AC8, #A855F7) !important;
        border-radius: 10px !important;
        height: 8px !important;
    }
    
    .stProgress > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        height: 8px !important;
    }
    
    /* Success message styling */
    .stSuccess {
        background: rgba(76, 175, 80, 0.1) !important;
        border: 1px solid rgba(76, 175, 80, 0.3) !important;
        border-radius: 12px !important;
        color: #4CAF50 !important;
        font-weight: 600 !important;
    }
    
    /* Info message styling */
    .stInfo {
        background: rgba(33, 150, 243, 0.1) !important;
        border: 1px solid rgba(33, 150, 243, 0.3) !important;
        border-radius: 12px !important;
        color: #2196F3 !important;
        font-weight: 600 !important;
    }
    
    /* Error message styling */
    .stError {
        background: rgba(244, 67, 54, 0.1) !important;
        border: 1px solid rgba(244, 67, 54, 0.3) !important;
        border-radius: 12px !important;
        color: #F44336 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background: rgba(10, 10, 10, 0.95) !important;
        border-right: 1px solid rgba(129, 74, 200, 0.2) !important;
    }
    
    .stSidebar .stSelectbox label,
    .stSidebar .stCheckbox label,
    .stSidebar .stTextInput label,
    .stSidebar .stNumberInput label {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 600 !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(129, 74, 200, 0.2) !important;
    }
    
    /* Chart container */
    .stPlotlyChart {
        background: transparent !important;
        border-radius: 16px !important;
    }
    
    /* Custom spacing */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .results-container {
        animation: slideIn 0.6s ease-out;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-title {
            font-size: 36px;
        }
        
        .overall-score {
            font-size: 48px;
        }
        
        .content-card {
            padding: 24px;
        }
        
        .header-container {
            padding: 24px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    st.markdown("""
    <div class="header-container">
        <div class="logo-section">
            <div class="logo-icon">⚡</div>
            <div>
                <h1 class="main-title">ScoreScope<sup style="font-size: 20px; opacity: 0.8;">AI</sup></h1>
                <p class="main-subtitle">AI-Powered PDF Evaluation and Scoring Platform</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Load enhanced styling
load_enhanced_css()

# Create header
create_header()

# Default categories with weights
DEFAULT_CATEGORIES = {
    "Requirements Fulfillment": 25,
    "Content Quality & Depth": 20,
    "Clarity & Communication": 18,
    "Structure & Organization": 15,
    "Critical Thinking": 12,
    "Presentation & Format": 10
}

# Sidebar configuration (collapsed by default for clean look)
with st.sidebar:
    st.markdown("### Configuration")
    eval_style = st.selectbox("Evaluation Style", ["balanced", "strict", "encouraging"])
    
    if st.checkbox("Customize Categories"):
        st.markdown("#### Edit Evaluation Categories")
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

# Main content area
col1, col2 = st.columns([1, 1], gap="large")

# Task Instructions section
with col1:
    st.markdown("""
    <div class="content-card">
        <h2 class="section-title">
            <div class="section-icon">📝</div>
            Task Instructions
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    task_outline = st.text_area(
        "Describe what you were asked to do:",
        placeholder="Enter the assignment instructions, job requirements, or evaluation criteria here...\n\nExample: Analyze a company's compliance program and provide recommendations for improvement based on regulatory requirements.",
        height=200,
        key="task_input",
        label_visibility="collapsed"
    )

# Upload section
with col2:
    st.markdown("""
    <div class="content-card">
        <h2 class="section-title">
            <div class="section-icon">📄</div>
            Upload Your Work
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_pdf = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Maximum file size: 200MB • Supported format: PDF",
        label_visibility="collapsed"
    )
    
    if uploaded_pdf:
        st.success(f"Successfully uploaded: {uploaded_pdf.name} ({uploaded_pdf.size / (1024*1024):.1f}MB)")

# Analysis button and results
if uploaded_pdf and task_outline:
    if st.button("Analyze with ScoreScope AI", key="analyze_btn"):
        start_time = time.time()
        file_hash = get_file_hash(uploaded_pdf)

        # Processing section
        st.markdown("""
        <div class="processing-container">
            <div class="processing-text">Processing your submission...</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        steps = [
            "Extracting text from PDF...",
            "Analyzing content structure...",
            "Evaluating against requirements...",
            "Generating category scores...",
            "Preparing detailed feedback..."
        ]
        
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) * 20)
            time.sleep(0.6)  # Realistic processing feel
        
        # Extract and analyze
        submission_text = extract_text_from_pdf(file_hash, uploaded_pdf, max_pages)
        if not submission_text:
            st.error("Failed to extract text from PDF. Please try again with a different file.")
            st.stop()

        ai_response = get_ai_feedback(task_outline, submission_text, categories, eval_style)
        if ai_response.startswith("ERROR"):
            st.error(ai_response)
            st.stop()

        # Parse results
        scores = parse_scores_enhanced(ai_response, categories)
        feedback_data = extract_enhanced_feedback(ai_response)
        weighted_score = calculate_weighted_score(scores, categories)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()

        # Display results
        processing_time = time.time() - start_time
        
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        # Overall score display
        st.markdown(f"""
        <div class="score-display">
            <div class="overall-score">{weighted_score}/10</div>
            <div class="score-label">Overall Score • Processed in {processing_time:.1f}s</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Radar chart
        st.plotly_chart(create_enhanced_radar_chart(scores), use_container_width=True, key="radar_chart")
        
        # Detailed category analysis
        st.markdown("### Detailed Category Analysis")
        
        for category, (score, explanation) in scores.items():
            with st.expander(f"{category}: {score}/10", expanded=False):
                st.markdown(f"**Weight:** {categories[category]}%")
                st.markdown(f"**Analysis:** {explanation}")
        
        # Overall assessment and action plan
        st.markdown("### Overall Assessment")
        st.write(feedback_data["overall"])
        
        st.markdown("### Action Plan")
        for i, action in enumerate(feedback_data["actions"], 1):
            st.markdown(f"**{i}.** {action}")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Score history tracking
        if "evaluation_history" not in st.session_state:
            st.session_state.evaluation_history = []
        
        st.session_state.evaluation_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "overall_score": weighted_score,
            **{cat: score for cat, (score, _) in scores.items()}
        })

        # Show progress over time if multiple evaluations
        if len(st.session_state.evaluation_history) > 1:
            st.markdown("### Your Progress Over Time")
            st.plotly_chart(create_score_history_chart(st.session_state.evaluation_history), use_container_width=True)
            
            # History table
            df_history = pd.DataFrame(st.session_state.evaluation_history)
            st.dataframe(df_history, use_container_width=True)

        # Export options
        with st.expander("Export Results", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                export_data = {
                    "task": task_outline,
                    "scores": {cat: score for cat, (score, _) in scores.items()},
                    "weighted_score": weighted_score,
                    "feedback": feedback_data,
                    "processing_time": f"{processing_time:.1f}s",
                    "timestamp": datetime.now().isoformat()
                }
                st.download_button(
                    "Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"scorescope_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                report = f"""SCORESCOPE EVALUATION REPORT

Overall Score: {weighted_score}/10
Processing Time: {processing_time:.1f}s

CATEGORY SCORES:
""" + "\n".join([f"- {cat}: {score}/10 (Weight: {categories[cat]}%)" for cat, (score, _) in scores.items()]) + f"""

OVERALL ASSESSMENT:
{feedback_data['overall']}

ACTION PLAN:
""" + "\n".join([f"{i}. {action}" for i, action in enumerate(feedback_data['actions'], 1)])
                
                st.download_button(
                    "Download Report",
                    data=report,
                    file_name=f"scorescope_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

        # Show raw AI response if requested
        if show_raw_response:
            with st.expander("Raw AI Response (Debug)"):
                st.text(ai_response)

elif uploaded_pdf or task_outline:
    st.info("Please provide both task instructions and upload a PDF to begin analysis.")
else:
    # Demo section when no inputs
    st.markdown("---")
    st.markdown("### See ScoreScope in Action")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Processing", "19.2s", "Fast Analysis")
    
    with col2:
        st.metric("Scoring Categories", "6", "Comprehensive")
    
    with col3:
        st.metric("Maximum File Size", "200MB", "Large Documents")
    
    st.markdown("### Perfect For:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Job Seekers**
        - Resume optimization and feedback
        - Cover letter evaluation
        - Application materials review
        
        **Students**
        - Assignment scoring and improvement
        - Essay evaluation and guidance
        - Project assessment
        """)
    
    with col2:
        st.markdown("""
        **Startups and Professionals**
        - Pitch deck review and refinement
        - Business plan evaluation
        - Grant application scoring
        
        **Hiring Teams**
        - Take-home assignment evaluation
        - Portfolio assessment
        - Interview material review
        """)