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

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* Main Background - Animated Gradient */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgb(17, 24, 39) 0%, rgb(17, 24, 39) 90%);
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f3f4f6;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(to right, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    
    /* Glassmorphism Cards */
    .claim-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .claim-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Status Badges */
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-Verified {
        background: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        border: 1px solid #22c55e;
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.3);
    }
    .badge-Inaccurate {
        background: rgba(251, 146, 60, 0.2);
        color: #fb923c;
        border: 1px solid #f97316;
    }
    .badge-False {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid #ef4444;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }
    
    /* Card Text */
    .claim-text {
        font-size: 1.15em;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .reason-text {
        font-size: 0.95em;
        color: #94a3b8;
        line-height: 1.6;
    }
    
    /* Links */
    .source-link {
        color: #60a5fa;
        text-decoration: none;
        font-size: 0.85em;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 6px;
        background: rgba(96, 165, 250, 0.1);
        transition: background 0.2s;
    }
    .source-link:hover {
        background: rgba(96, 165, 250, 0.2);
        color: #93c5fd;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 800 !important;
        background: linear-gradient(to bottom, #f8fafc, #cbd5e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: white;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: Configuration ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6821/6821002.png", width=100)
    st.title("FactCheck Pro")
    st.markdown("Automated verification agent for documents.")
    
    st.markdown("---")
    
    # 🔑 Session State Management for Keys
    if "openai_api_key" not in st.session_state:
        try:
            st.session_state.openai_api_key = st.secrets.get("OPENAI_API_KEY", "")
        except:
            st.session_state.openai_api_key = ""
            
    if "tavily_api_key" not in st.session_state:
        try:
            st.session_state.tavily_api_key = st.secrets.get("TAVILY_API_KEY", "")
        except:
            st.session_state.tavily_api_key = ""

    # Only show inputs if keys are missing from Secrets
    if not st.session_state.openai_api_key:
        st.session_state.openai_api_key = st.text_input("OpenAI API Key", type="password", help="Required for extraction.")
        
    if not st.session_state.tavily_api_key:
        st.session_state.tavily_api_key = st.text_input("Tavily API Key", type="password", help="Required for search.")
    
    openai_key = st.session_state.openai_api_key
    tavily_key = st.session_state.tavily_api_key
    
    if openai_key and tavily_key:
        st.success("✅ API Keys Configured")
    else:
        st.warning("⚠️ Waiting for Keys")
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
            st.caption(f"Debug: Extracted {len(text)} characters from PDF.")
            
            # 2. Extract Claims
            claims = checker.extract_claims(text)
            
        if not claims:
            st.error("No verifiable claims found.")
            st.markdown("### Debug: Generated Text Snippet")
            st.text(text[:1000]) # Show what was actually read
        else:
            st.success(f"Found {len(claims)} claims. Verifying now...")
            
            # 3. Verify Claims (Sequential - Safer for API Limits)
            if len(claims) == 1 and claims[0].startswith("SYSTEM_ERROR"):
                st.error(f"Extraction Error: {claims[0]}")
                st.warning("Please check your API Key and try again.")
            else:
                results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, claim in enumerate(claims):
                    # Verify
                    status_text.caption(f"Verifying claim {i+1}/{len(claims)}...")
                    result = checker.verify_claim(claim)
                    results.append(result)
                    
                    # Update Progress
                    progress_bar.progress((i + 1) / len(claims))
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
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
                    status_label = "VERIFIED" if res['status'] == 'Verified' else "INACCURATE" if res['status'] == 'Inaccurate' else "FALSE" if res['status'] == 'False' else "UNCERTAIN"
                    
                    st.markdown(f"""
                    <div class="claim-card {status_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span class="status-badge badge-{res['status']}">{status_label}</span>
                        </div>
                        <div class="claim-text">{res['claim']}</div>
                        <div class="reason-text">{res['reason']}</div>
                        <div style="margin-top: 15px; text-align: right;">
                            <a href="{res['source_url']}" target="_blank" class="source-link">↗ Verify Source</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

elif not uploaded_file:
    st.info("👆 Please upload a PDF to begin.")
elif not (openai_key and tavily_key):
    st.info("👈 Please enter your API keys in the sidebar.")
