class DefenderAgent:
    def argue(self, evidence, confidence):
        arguments = []

        for e in evidence:
            if e["agent"] == "risk_agent" and e.get("geo_risk", 0) < 0.4:
                arguments.append("Low geographic risk")

            if e["agent"] == "transaction_agent" and e.get("severity", 0) < 0.4:
                arguments.append("Transaction anomaly severity is low")

            if e["agent"] == "user_behavior_agent" and e.get("deviation", 0) < 0.5:
                arguments.append("User behavior is within acceptable variance")

        if confidence > 0.75:
            arguments.append("System confidence is strong")

        return arguments or ["No strong indicators of fraud"]