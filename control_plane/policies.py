class PolicyEngine:
    def __init__(self):
        self.max_external_calls = 3
        self.allow_auto_decision = True
        self.min_confidence_threshold = 0.6

    def validate(self, context):
        if context["external_calls"] > self.max_external_calls:
            return False, "Exceeded external API call limit"
        
        if (
            context["confidence"] < self.min_confidence_threshold and self.allow_auto_decision
        ):
            return False, "Low confidence - human review required"
        
        return True, "Policy validation passed"