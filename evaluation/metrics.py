import numpy as np
from sklearn.metrics import roc_auc_score

def normalize_decision(decision):
    if isinstance(decision, dict):
        return decision.get("status")
    return decision

def compute_metrics(results):
    if not results:
        return {"performance": {}, "governance": {}}

    # --- Stage 1: Performance Metrics ---
    tp = fp = tn = fn = 0
    y_true = []
    y_scores = []

    for r in results:
        is_fraud = r["is_fraud"]
        decision = normalize_decision(r["decision"])
        confidence = r.get("confidence", 0.5)
        
        y_true.append(1 if is_fraud else 0)
        score = confidence if decision in ["DECLINED", "HUMAN_REVIEW"] else (1 - confidence)
        y_scores.append(score)

        if is_fraud:
            if decision in ["DECLINED", "HUMAN_REVIEW"]:
                tp += 1
            else:
                fn += 1
        else:
            if decision in ["DECLINED", "HUMAN_REVIEW"]:
                fp += 1
            else:
                tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0
    
    try:
        auc = roc_auc_score(y_true, y_scores) if len(set(y_true)) > 1 else 0.5
    except:
        auc = 0.5

    performance = {
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "auc_roc": auc,
        "detection_rate": tp / (tp + fn) if (tp + fn) else 0
    }

    # --- Stage 2: Governance Metrics ---
    steps = [r.get("steps_taken", 0) for r in results]
    gov_scores = [r.get("governance_score", 1.0) for r in results]
    rationale_lengths = [len(str(r.get("rationale", ""))) for r in results]
    valid_logic_count = sum(1 for r in results if r.get("logic_validation") == "valid")
    
    escalation_rate = sum(
        1 for r in results
        if normalize_decision(r["decision"]) == "HUMAN_REVIEW"
    ) / len(results)

    governance = {
        "avg_steps_to_decision": np.mean(steps),
        "governance_compliance_score": np.mean(gov_scores),
        "interpretability_proxy_score": np.mean(rationale_lengths) / 100.0, # Scaled length
        "logical_integrity_rate": valid_logic_count / len(results),
        "human_escalation_rate": escalation_rate
    }

    return {
        "performance": performance,
        "governance": governance
    }