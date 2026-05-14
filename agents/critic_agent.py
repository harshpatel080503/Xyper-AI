import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

class CriticAgent:
    def __init__(self, llm=None):
        api_key = os.getenv("OLLAMA_API_KEY")
        if not api_key:
            logging.error("OLLAMA_API_KEY is missing from environment!")
        
        # Using ChatOllama with the official cloud base_url and headers
        self.llm = llm or ChatOllama(
            model="gpt-oss:120b-cloud",
            base_url="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"},
            temperature=0
        )

    def review(self, evidence, case, governance_mode=False):
        case_str = str(case)
        evidence_str = str(evidence)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Fraud Audit Specialist. Review the evidence provided and calibrate the final decision.
            
            Check for:
            1. Safety: No sensitive user data leaks.
            2. Bias: Neutral analysis.
            3. Logic: Evidence must support the decision.
            
            Output strictly in JSON:
            {{
                "governance_score": 0.0-1.0,
                "logic_validation": "valid/invalid",
                "confidence_adjustment": float,
                "feedback": "string"
            }}"""),
            ("user", "Fraud Case: {case}\nEvidence: {evidence}")
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages(case=case_str, evidence=evidence_str))
            content = response.content if hasattr(response, 'content') else str(response)
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            data = json.loads(content)
            return {
                "governance_score": data.get("governance_score", 0.8),
                "logic_validation": data.get("logic_validation", "valid"),
                "confidence_adjustment": data.get("confidence_adjustment", 0.0),
                "feedback": data.get("feedback", "")
            }
        except Exception as e:
            # Enhanced logging to debug the 401/Sync error
            logging.error(f"Critic LLM Error: {e}")
            return {
                "governance_score": 0.5,
                "confidence_adjustment": 0.0,
                "logic_validation": "valid",
                "feedback": f"LLM Error: {str(e)[:100]}"
            }