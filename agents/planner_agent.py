class PlannerAgent:
    def plan(self, fraud_case):
        plan = []

        if fraud_case.amount > 10000:
            plan.append("transaction_analysis")
        
        plan.append("user_behavior")

        if fraud_case.transaction_type in ["TRANSFER", "CASH_OUT"]:
            plan.append("risk_intelligence")

        return plan