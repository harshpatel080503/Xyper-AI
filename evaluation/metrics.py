def normalize_decision(decision):
    if isinstance(decision, dict):
        return "ESCALATED"
    return decision

def compute_metrics(results):
    tp = fp = tn = fn = escalations = 0

    for r in results:
        is_fraud = r["is_fraud"]
        decision = r["decision"]

        if decision == "ESCALATED":
            escalations += 1
            continue

        if decision == "APPROVED":
            if is_fraud:
                fn += 1  # fraud missed
            else:
                tn += 1
        else:  # future: DECLINED
            if is_fraud:
                tp += 1
            else:
                fp += 1

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    escalation_rate = escalations / len(results)

    return {
        "total_cases": len(results),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": precision,
        "recall": recall,
        "escalation_rate": escalation_rate
    }