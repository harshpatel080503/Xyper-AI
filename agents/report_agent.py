class ReportAgent:
    def generate(self, fraud_case, evidence, decision):
        return {
            "transaction_id": fraud_case.transaction_id,
            "decision": decision,
            "evidence": evidence
        }