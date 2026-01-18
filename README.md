# ✅ FactCheck Pro

**A Professional AI-Powered Document Verification Agent.**  

## 📌 Overview
**FactCheck Pro** is a web application that automates the tedious process of fact-checking documents. It ingests a PDF, identifies statistical and verifiable claims using GPT-4o, and cross-references them against live web data using the Tavily Search API.

**Key Features:**
*   **Context-Aware Extraction**: Understands complete sentences (e.g., "GDP grew by 5%" vs just "5%").
*   **Live Verification**: Searches the real-time web for evidence.
*   **Strict Verdicts**: Classifies claims ONLY as **Verified**, **Inaccurate**, or **False**.
*   **Modern UI**: Glassmorphism design with a dark mode aesthetic.
*   **One-Click Use**: Configured with Streamlit Secrets for instant access.

---

## 🛠️ How It Works

1.  **Ingestion**: The app reads your uploaded PDF (`pypdf`).
2.  **Extraction Agent**: 
    *   Uses `GPT-4o-mini` to scan the text.
    *   Extracts **standalone claims** focusing on stats, dates, and figures.
3.  **Verification Agent**: 
    *   Takes each claim and performs a live **Tavily Search**.
    *   Feeds the search results back to the LLM.
    *   The LLM compares the claim vs. evidence and assigns a verdict.
4.  **Reporting**: 
    *   **✅ Verified**: The numbers match.
    *   **⚠️ Inaccurate**: The claim is outdated, wrong, or insufficient evidence exists.
    *   **❌ False**: Direct contradiction found.

---

## 💻 Tech Stack
*   **Frontend**: Streamlit (Python)
*   **Logic**: LangChain
*   **LLM**: OpenAI GPT-4o-mini
*   **Search**: Tavily Search API

## 🔧 Installation & Local Setup

1.  **Clone the Repo**
    ```bash
    git clone https://github.com/ABHIGHUDAIYA/FactCheck-Pro.git
    cd fact-check-pro
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Keys (Secrets)**
    Create a file at `.streamlit/secrets.toml`:
    ```toml
    OPENAI_API_KEY = "sk-..."
    TAVILY_API_KEY = "tvly-..."
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure
*   `app.py`: Main frontend application and UI logic.
*   `fact_checker.py`: Core AI logic (Extraction & Verification classes).
*   `requirements.txt`: List of Python dependencies.
*   `README.md`: Documentation.

## 📝 Evaluation Notes
*   **Accuracy**: The prompt is strictly engineered to avoid "Uncertain" answers. If evidence is missing, it defaults to "Inaccurate" to be safe.
*   **Speed**: Uses sequential processing to respect API rate limits (avoiding 429 errors).
*   **Context**: The extract logic grabs full sentences to ensure the verificator understands *what* the number refers to.
