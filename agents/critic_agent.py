class CriticAgent:
    def review(self, evidence):
        if len(evidence) < 2:
            return "NEEDS_HUMAN_REVIEW"
        return "APPROVED"