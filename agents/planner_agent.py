class PlannerAgent:
    def plan(self, fraud_case):
        plan = []

        # Always analyze transaction
        plan.append("transaction")

        # Always check user behavior
        plan.append("user")

        # Add risk if amount large or transfer
        if fraud_case.amount > 10000 or fraud_case.transaction_type in ["TRANSFER", "CASH_OUT"]:
            plan.append("risk")

        return plan