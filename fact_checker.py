import os
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.tools.tavily_search import TavilySearchResults
from pypdf import PdfReader
import tempfile

class FactChecker:
    def __init__(self, openai_api_key, tavily_api_key):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini", 
            api_key=openai_api_key
        )
        self.search = TavilySearchResults(tavily_api_key=tavily_api_key, max_results=3)

    def extract_text_from_pdf(self, uploaded_file):
        """Extracts text from a persistent PDF file path or BytesIO object."""
        try:
            # Handle UploadedFile (BytesIO) from Streamlit
            if hasattr(uploaded_file, "read"):
                # Reset pointer just in case
                uploaded_file.seek(0)
                pdf_reader = PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
                return text
            # Handle File Path (String)
            else:
                loader = PyPDFLoader(uploaded_file)
                pages = loader.load()
                return "".join([p.page_content for p in pages])
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def extract_claims(self, text):
        """Extracts verifying claims from the text using LLM."""
        from langchain_core.output_parsers import StrOutputParser
        import json
        import re

        # Clean text to remove excessive newlines/spacing issues from PDF
        clean_text = re.sub(r'\s+', ' ', text).strip()

        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert fact-checker. 
            Extract specific, verifiable claims from the text below.
            
            CRITICAL RULES:
            1. Extract **complete, standalone sentences** that contain the claim. Do not extract fragments. 
               - BAD: "5%"
               - GOOD: "Real GDP growth for the full year 2025 closed at -1.5%."
            2. Focus on: Statistics, Dates, Financial Figures, Technical Specs.
            3. Ignore opinions or general fluff.
            
            Return ONLY a valid JSON object with this structure:
            {{
                "claims": ["claim 1", "claim 2", ...]
            }}
            
            Text:
            {text}
            """
        )
        
        # Use StrOutputParser for raw control
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            # Invoking
            raw_response = chain.invoke({"text": clean_text[:50000]})
            
            # Clean potential markdown fences
            json_str = raw_response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
                
            parsed = json.loads(json_str)
            return parsed.get("claims", [])
        except Exception as e:
            return [f"SYSTEM_ERROR: {str(e)}"]

    def verify_claim(self, claim):
        """Verifies a single claim against web search results."""
        # 1. Search
        try:
            search_results = self.search.invoke(claim)
        except Exception as e:
            return {
                "claim": claim,
                "status": "Inaccurate",
                "reason": f"Search failed: {str(e)}",
                "source_url": "N/A"
            }
        
        # 2. Verify with LLM
        verification_prompt = ChatPromptTemplate.from_template(
            """
            You are a strict fact-checker. 
            Claim: "{claim}"
            
            Live Web Search Results:
            {search_results}
            
            Task:
            1. Compare the claim against the search results context.
            2. Determine the status. YOU MUST CHOOSE ONE OF THE FOLLOWING EXACTLY:
               - "Verified": The claim is supported by the data.
               - "Inaccurate": The claim is wrong, outdated, OR you cannot find sufficient evidence.
               - "False": The claim is directly contradicted.
            
            CRITICAL: DO NOT return "Uncertain" or "Unverified". If you don't know, use "Inaccurate".
            
            Return JSON:
            {{
                "claim": "{claim}",
                "status": "Verified" | "Inaccurate" | "False",
                "reason": "Brief explanation...",
                "source_url": "URL from results"
            }}
            """
        )
        
        chain = verification_prompt | self.llm | JsonOutputParser()
        try:
            result = chain.invoke({"claim": claim, "search_results": search_results})
            return result
        except Exception as e:
            return {
                "claim": claim,
                "status": "Error",
                "reason": str(e),
                "source_url": ""
            }
