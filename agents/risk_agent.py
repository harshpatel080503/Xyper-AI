import random

class RiskAgent:
    def analyze(self, fraud_case):
        risk_score = random.uniform(0, 1)

        return {
            "agent": "risk_agent",
            "geo_risk": risk_score,
        }