class PolicyEngine:
    def __init__(self):
        self.max_external_calls = 5
        self.allow_auto_decision = True
        self.min_confidence_threshold = 0.7
        self.max_auto_approve_amount = 500000.0 # Regulatory cap for auto-approval
        self.high_risk_types = ["CASH_OUT", "TRANSFER"]

    def validate(self, context):
        fraud_case = context.get("fraud_case")
        
        if context["external_calls"] > self.max_external_calls:
            return False, "Safety trigger: Exceeded maximum investigation steps (potential infinite loop)"
        
        if context["confidence"] < self.min_confidence_threshold:
            return False, f"Confidence {context['confidence']:.2f} is below safety threshold ({self.min_confidence_threshold})"
        
        if fraud_case:
            if fraud_case.amount > self.max_auto_approve_amount:
                return False, f"Transaction amount {fraud_case.amount} exceeds auto-approval limit of {self.max_auto_approve_amount}"
            
            if fraud_case.transaction_type in self.high_risk_types and fraud_case.amount > 100000.0:
                return False, f"High-risk transaction type '{fraud_case.transaction_type}' requires manual review for amounts > 100,000"
        
        return True, "Policy validation passed: Transaction meets all safety and regulatory criteria."