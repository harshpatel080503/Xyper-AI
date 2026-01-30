class TransactionAgent:
    def analyze(self, fraud_case):
        anomalies = []

        if fraud_case.amount > fraud_case.origin_balance:
            anomalies.append("Amount exceeds origin balance")

        if fraud_case.amount > 5 * fraud_case.destination_balance:
            anomalies.append("Unusual destination balance jump")

        return {
            "agent": "transaction_agent",
            "anomalies": anomalies,
            "severity": min(len(anomalies) / 3, 1.0)
        }