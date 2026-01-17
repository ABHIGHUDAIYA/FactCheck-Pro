# FactCheck Pro - Automated Claim Verification

## Overview
FactCheck Pro is an AI-powered web application that automates the verification of claims within PDF documents. It extracts statistical claims, dates, and figures, then cross-references them against live web data to verify their accuracy.

## Features
*   **PDF Ingestion**: Upload any PDF document (reports, articles, drafts).
*   **Smart Extraction**: Uses GPT-4 to identify verifiable claims (ignoring opinions).
*   **Live Verification**: Uses Tavily Search API to find real-time sources.
*   **Verdict Engine**: Classifies claims as **Verified**, **Inaccurate**, or **False** with reasoning.

## Tech Stack
*   **Frontend**: Streamlit (Python-based Web UI)
*   **LLM**: OpenAI GPT-4 Turbo
*   **Search**: Tavily Search API
*   **Orchestration**: LangChain

## Setup & Running Locally

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd fact-check-pro
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App**
    ```bash
    streamlit run app.py
    ```

4.  **Enter API Keys**
    *   The app will prompt you for your OpenAI and Tavily API keys in the sidebar.

## Deployment
This app is ready for **Streamlit Cloud**:
1.  Push this code to GitHub.
2.  Login to [share.streamlit.io](https://share.streamlit.io).
3.  Deploy the repository.
4.  Add your API Keys in the app sidebar (or in Streamlit Secrets).

## Evaluation Criteria Handling
*   **Extract**: Specifically targets numbers/dates.
*   **Verify**: Searches live web (not just training data).
*   **Report**: clear UI with flags (Red/Green/Orange).
