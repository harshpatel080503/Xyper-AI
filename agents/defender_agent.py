import json

class DefenderAgent:
    def __init__(self, llm=None):
        self.llm = llm

    def argue(self, evidence, confidence):
        """
        AI-driven defense arguments based on evidence.
        """
        if not self.llm:
            # Fallback to rule-based
            arguments = []
            for e in evidence:
                if e["agent"] == "risk_agent" and e.get("geo_risk", 0) < 0.4:
                    arguments.append("Low geographic risk")
            return arguments or ["No strong indicators of fraud"]

        evidence_str = json.dumps(evidence, indent=2)
        
        prompt = f"""
        You are a Defense Solicitor in a Fraud Investigation system. Your goal is to build a case AGAINST fraud based on the evidence. Focus on finding reasons why this transaction might be legitimate.
        
        Evidence:
        {evidence_str}
        
        System Confidence: {confidence}
        
        Task:
        1. Identify specific indicators of legitimacy from the evidence.
        2. Explain why these indicators suggest the transaction may be safe.
        3. Challenge the suspicious findings if possible (e.g., "The high amount is not necessarily fraud if the user has a history of high balance").
        
        Output:
        A list of string arguments, e.g. ["Argument 1", "Argument 2"]
        Return ONLY the list.
        """
        
        response = self.llm.invoke(prompt)
        try:
            content = response.content if hasattr(response, 'content') else str(response)
            if "[" in content and "]" in content:
                content = content[content.find("["):content.rfind("]")+1]
                return json.loads(content)
            return [content.strip()]
        except Exception:
            return ["No significant fraud risk indicators found in evidence."]