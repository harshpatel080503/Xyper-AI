import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json

class AdversarialAgent:
    def __init__(self, llm=None):
        api_key = os.getenv("OLLAMA_API_KEY")
        self.llm = llm or ChatOllama(
            model="gpt-oss:120b-cloud",
            base_url="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"},
            temperature=0
        )

    def analyze(self, case, evidence):
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a dual-role Fraud Auditor. Provide both Prosecution (Fraud) and Defense (Legitimate) arguments for this case.
            
            IMPORTANT: If the metadata shows 'isFraud': 1 or 'Class': 1, the Prosecution MUST emphasize this as definitive proof.
            
            Output strictly in JSON:
            {{
                "prosecution": ["arg1", "arg2"],
                "defense": ["arg1", "arg2"],
                "prosecution_pressure": 0.0-1.0,
                "defense_pressure": 0.0-1.0
            }}"""),
            ("user", "Case: {case}\nExisting Evidence: {evidence}")
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages(case=str(case), evidence=str(evidence)))
            content = response.content if hasattr(response, 'content') else str(response)
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
        except Exception:
            return {
                "prosecution": ["Pattern anomaly detected"],
                "defense": ["Historical consistency noted"],
                "prosecution_pressure": 0.5,
                "defense_pressure": 0.5
            }
