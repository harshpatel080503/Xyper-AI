import json

class ProsecutorAgent:
    def __init__(self, llm=None):
        self.llm = llm

    def argue(self, evidence, confidence):
        """
        AI-driven prosecution arguments based on evidence.
        """
        if not self.llm:
            # Fallback to rule-based
            arguments = []
            for e in evidence:
                if e["agent"] == "transaction_agent" and e.get("severity", 0) > 0.3:
                    arguments.append("Transaction shows abnormal balance behavior")
            return arguments or ["Insufficient evidence for strong fraud claim"]

        evidence_str = json.dumps(evidence, indent=2)
        
        prompt = f"""
        You are a Prosecutor in a Fraud Investigation system. Your goal is to build a case FOR fraud based on the evidence.
        
        Evidence:
        {evidence_str}
        
        System Confidence: {confidence}
        
        Task:
        1. Identify specific indicators of fraud from the evidence.
        2. Explain why these indicators are suspicious in the context of banking safety.
        3. Keep arguments concise and objective.
        
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
            return ["Evidence suggests potential fraud based on risk indicators."]