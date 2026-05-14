import numpy as np

class UserBehaviorAgent:
    def analyze(self, fraud_case, user_history):
        """
        Analyzes transaction against user's historical behavior.
        """
        insights = []
        
        amounts = user_history["amount"].values
        avg_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        max_amount = np.max(amounts)

        # Deviation logic
        z_score = (fraud_case.amount - avg_amount) / (std_amount if std_amount > 0 else 1)
        
        if fraud_case.amount > max_amount * 1.5:
            insights.append(f"Transaction amount ({fraud_case.amount}) is 50% higher than historical max ({max_amount})")
        
        if z_score > 3:
            insights.append(f"Significant statistical anomaly: amount is {z_score:.1f} standard deviations from mean")
        
        # Simple velocity check (mocked for now as we don't have timestamps in this simple df)
        # But we could check transaction frequency if available

        # Map insights to a deviation score [0, 1]
        deviation = min(1.0, max(0.0, z_score / 5.0)) if z_score > 0 else 0.0

        return {
            "agent": "user_behavior_agent",
            "insights": insights,
            "deviation": deviation,
            "metrics": {
                "avg_historical": avg_amount,
                "z_score": z_score
            }
        }