import random

class FraudsterAgent:
    def evade(self, fraud_case):
        tactics = []

        if fraud_case.amount > 5000:
            fraud_case.amount *= random.uniform(0.4, 0.8)
            tactics.append("amount_splitting")

        if fraud_case.transaction_type == "TRANSFER":
            fraud_case.transaction_type = "PAYMENT"
            tactics.append("type_morphing")

        return fraud_case, tactics