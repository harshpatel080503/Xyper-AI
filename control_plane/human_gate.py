def human_review_required(reason: str):
    return {
        "status": "HUMAN_REVIEW",
        "reason": reason
    }