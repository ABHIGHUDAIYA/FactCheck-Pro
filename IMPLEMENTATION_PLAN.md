
# Implementation Plan: Fact-Checking Web App

## Tech Stack
*   **Frontend**: Streamlit (Chosen for speed, "simple" requirement, and ease of Python integration).
*   **Logic**: LangChain + OpenAI (GPT-4o or GPT-3.5-turbo).
*   **Search**: Tavily API (Optimized for LLM agents).
*   **Deployment**: Streamlit Cloud (Fastest route to live URL).

## File Structure
*   `app.py`: Main application UI and orchestration.
*   `fact_checker.py`: Core logic for extraction and verification.
*   `requirements.txt`: Python dependencies.
*   `README.md`: Instructions for the user and evaluator.

## Features
1.  **PDF Upload**: Drag & Drop interface.
2.  **Claim Extraction**: LLM identifies checks (Stats, Dates, Figures).
3.  **Verification Agent**: Search web (Tavily) -> Compare -> Verdict.
4.  **Reporting**: Clean UI with verifying/inaccurate flags and sources.

## User Action Required
*   You will need an **OpenAI API Key**.
*   You will need a **Tavily API Key** (Free tier available).
*   I will verify these keys are present in the UI or Environment.
