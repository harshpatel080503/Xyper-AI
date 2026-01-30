class ProsecutorAgent:
    def argue(self, evidence, confidence):
        arguments = []

        for e in evidence:
            if e["agent"] == "transaction_agent" and e.get("severity", 0) > 0.3:
                arguments.append("Transaction shows abnormal balance behavior")

            if e["agent"] == "user_behavior_agent" and e.get("deviation", 0) > 0.4:
                arguments.append("User behavior deviates significantly from history")

            if e["agent"] == "risk_agent" and e.get("geo_risk", 0) > 0.7:
                arguments.append("High geographic risk detected")

        if confidence < 0.7:
            arguments.append("Overall confidence is not strong")

        return arguments or ["Insufficient evidence for strong fraud claim"]