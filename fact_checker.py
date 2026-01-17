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
            model="gpt-4-turbo-preview", 
            api_key=openai_api_key
        )
        self.search = TavilySearchResults(api_key=tavily_api_key, max_results=3)

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
        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert fact-checker. Your task is to identify specific, verifiable claims 
            within the provided text. Focus on:
            - Statistics (numbers, percentages, financial figures)
            - Dates and times
            - Specific technical specifications
            - Definitive historical or event-based statements

            Ignore opinions, general descriptions, or subjective statements.
            
            Return the result as a JSON object with a key 'claims', which is a list of strings.
            Limit to the top 10 most verifiable and critical claims to save time if the text is long.
            
            Text:
            {text}
            """
        )
        chain = prompt | self.llm | JsonOutputParser()
        try:
            # Chunk text if too huge (naive truncation for demo speed)
            response = chain.invoke({"text": text[:50000]})
            return response.get("claims", [])
        except Exception as e:
            print(f"Extraction Error: {e}")
            return []

    def verify_claim(self, claim):
        """Verifies a single claim against web search results."""
        # 1. Search
        search_results = self.search.invoke(claim)
        
        # 2. Verify with LLM
        verification_prompt = ChatPromptTemplate.from_template(
            """
            You are a strict fact-checker. 
            Claim: "{claim}"
            
            Live Web Search Results:
            {search_results}
            
            Task:
            1. Compare the claim against the search results.
            2. Determine the status:
               - "Verified": The claim matches the data found.
               - "Inaccurate": The claim is outdated, slightly wrong, or misleading.
               - "False": The claim is directly contradicted by evidence.
               - "Unverified": No sufficient evidence found.
            3. Provide a brief "reason" (1-2 sentences).
            4. Provide a "source_url" from the search results that best proves/disproves it.
            
            Return JSON:
            {{
                "claim": "{claim}",
                "status": "Verified" | "Inaccurate" | "False" | "Unverified",
                "reason": "...",
                "source_url": "..."
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
