import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class RationaleLLM:
    def __init__(self):
        api_key = os.getenv("OLLAMA_API_KEY")
        self.llm = ChatOllama(
            model="gpt-oss:120b-cloud",
            base_url="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"},
            temperature=0
        )

    def rewrite(self, rationale: str, confidence: float) -> str:
        """
        Rewrites a technical rationale into a formal, academic-grade explanation.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Financial Crimes Investigator. Generate a formal, evidentiary rationale for a fraud decision.
            Use a professional tone suitable for a conference paper. Avoid repetition.
            
            Format:
            1. Evidence Summary: ...
            2. Behavioral Analysis: ...
            3. Final Conclusion: ..."""),
            ("user", "Technical Rationale: {rationale}\nConfidence: {confidence}")
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages(rationale=rationale, confidence=confidence))
            return response.content.strip()
        except Exception:
            return f"Rationale: {rationale} (Confidence: {confidence})"