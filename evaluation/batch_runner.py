import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
from tqdm import tqdm
from evaluation.metrics import normalize_decision

def run_batch(cases, service):
    results = []

    for case in cases:
        report = service.investigate(case)

        decision = normalize_decision(report["decision"])

        results.append({
            "transaction_id": case.transaction_id,
            "decision": decision,
            "confidence": report.get("confidence"),
            "is_fraud": case.is_flagged
        })

    return results