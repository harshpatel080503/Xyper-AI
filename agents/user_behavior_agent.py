class UserBehaviorAgent:
    def analyze(self, fraud_case, user_history):
        insights = []

        avg_amount = user_history["amount"].mean()

        if fraud_case.amount > 3 * avg_amount:
            insights.append("Transaction much higher than user average")

        return {
            "agent": "user_behavior_agent",
            "insights": insights,
            "deviation": min(len(insights) / 2, 1.0)
        }