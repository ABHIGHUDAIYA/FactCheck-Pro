import streamlit as st
import pandas as pd
import time
from fact_checker import FactChecker

# --- Page Configuration ---
st.set_page_config(
    page_title="FactCheck Pro",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Feel ---
st.markdown("""
    <style>
    /* Main Background and Font */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Title Styling */
    h1 {
        color: #1a202c;
        font-weight: 800;
        letter-spacing: -0.025em;
    }
    
    /* Card Styling */
    .claim-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #cbd5e0;
        transition: transform 0.2s;
    }
    .claim-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Status Colors */
    .status-Verified { border-left-color: #48bb78; }
    .status-Inaccurate { border-left-color: #ed8936; }
    .status-False { border-left-color: #f56565; }
    
    /* Text Styling */
    .claim-text {
        font-size: 1.1em;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 8px;
    }
    .reason-text {
        font-size: 0.95em;
        color: #4a5568;
        margin-bottom: 12px;
    }
    .source-link {
        font-size: 0.85em;
        color: #3182ce;
        text-decoration: none;
        font-weight: 500;
    }
    .source-link:hover {
        text-decoration: underline;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #3182ce;
        color: white;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #2b6cb0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/9626/9626629.png", width=60)
    st.title("FactCheck Pro")
    st.markdown("Automated verification agent for documents.")
    
    st.markdown("---")
    
    st.markdown("### 🔑 API Configuration")
    openai_key = st.text_input("OpenAI API Key", type="password", help="Required for extraction and reasoning.")
    tavily_key = st.text_input("Tavily API Key", type="password", help="Required for live web search.")
    
    if not openai_key or not tavily_key:
        st.warning("Please enter both API keys to proceed.")
        
    st.markdown("---")
    st.markdown("### ℹ️ How it Works")
    st.info(
        "1. **Upload** a PDF document.\n"
        "2. **Extract** verifiable claims.\n"
        "3. **Verify** against live web data.\n"
        "4. **Report** with sources."
    )

# --- Main Interface ---
st.title("📄 Document Fact Checker")
st.markdown("Upload a document to cross-reference claims against the live web.")

uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"])

if uploaded_file and openai_key and tavily_key:
    # Initialize Logic
    checker = FactChecker(openai_key, tavily_key)
    
    # Process Button
    if st.button("Analyze Document", type="primary"):
        with st.spinner("🔍 Extracting text and identifying claims..."):
            # 1. Extract Text
            text = checker.extract_text_from_pdf(uploaded_file)
            
            # 2. Extract Claims
            claims = checker.extract_claims(text)
            
        if not claims:
            st.error("No verifiable claims found in the document.")
        else:
            st.success(f"Found {len(claims)} claims. Verifying now...")
            
            # 3. Verify Claims (with Progress Bar)
            results = []
            progress_bar = st.progress(0)
            
            for i, claim in enumerate(claims):
                # Verify
                result = checker.verify_claim(claim)
                results.append(result)
                progress_bar.progress((i + 1) / len(claims))
            
            # Clear progress
            progress_bar.empty()
            
            # --- Results Display ---
            st.markdown("### 📊 Verification Report")
            
            # Summary Metrics
            verified_count = sum(1 for r in results if r['status'] == 'Verified')
            inaccurate_count = sum(1 for r in results if r['status'] == 'Inaccurate')
            false_count = sum(1 for r in results if r['status'] == 'False')
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Verified", verified_count, delta_color="normal")
            col2.metric("Inaccurate", inaccurate_count, delta_color="inverse")
            col3.metric("False", false_count, delta_color="inverse")
            
            st.markdown("---")
            
            # Detailed Cards
            for res in results:
                status_class = f"status-{res['status']}"
                icon = "✅" if res['status'] == 'Verified' else "⚠️" if res['status'] == 'Inaccurate' else "❌" if res['status'] == 'False' else "❓"
                
                st.markdown(f"""
                <div class="claim-card {status_class}">
                    <div class="claim-text">{icon} {res['claim']}</div>
                    <div class="reason-text"><strong>Verdict:</strong> {res['status']}</div>
                    <div class="reason-text">{res['reason']}</div>
                    <a href="{res['source_url']}" target="_blank" class="source-link">🔗 Source Evidence</a>
                </div>
                """, unsafe_allow_html=True)

            # Raw Data Expander
            with st.expander("View Raw Data (JSON)"):
                st.json(results)

elif not uploaded_file:
    st.info("👆 Please upload a PDF to begin.")
elif not (openai_key and tavily_key):
    st.info("👈 Please enter your API keys in the sidebar.")
