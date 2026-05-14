class TransactionAgent:
    def analyze(self, fraud_case):
        amount = fraud_case.amount
        tx_type = fraud_case.transaction_type

        severity = 0.0

        # High-risk combination only (no standalone boosts)
        if amount > 200000 and tx_type in ["TRANSFER", "CASH_OUT"]:
            severity = 0.7

        elif amount > 100000 and tx_type in ["TRANSFER", "CASH_OUT"]:
            severity = 0.4

        else:
            severity = 0.1  # mild baseline anomaly

        # Cap severity
        severity = min(severity, 1.0)

        return {
            "agent": "transaction_agent",
            "severity": severity
        }
