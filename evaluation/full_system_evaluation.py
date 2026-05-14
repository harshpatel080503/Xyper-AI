import sys
import os
import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from tools.transaction_tools import load_transactions, create_fraud_case
from service.investigation_service import InvestigationService
from evaluation.batch_runner import run_batch
from evaluation.metrics import compute_metrics
from evaluation.metrics import normalize_decision


def compute_additional_metrics(results):
    confidences = []
    approvals = 0
    escalations = 0

    for r in results:
        if r["confidence"] is not None:
            confidences.append(r["confidence"])

        if r["decision"] == "APPROVED":
            approvals += 1
        elif normalize_decision(r["decision"]) == "HUMAN_REVIEW":
            escalations += 1

    total = len(results)

    avg_confidence = np.mean(confidences) if confidences else 0
    std_confidence = np.std(confidences) if confidences else 0

    return {
        "total_cases": total,
        "auto_approval_rate": approvals / total if total else 0,
        "escalation_rate": escalations / total if total else 0,
        "average_confidence": avg_confidence,
        "confidence_std_dev": std_confidence
    }


def main():
    print("Loading dataset...")
    df = load_transactions(
        "E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv"
    ).head(1000)  # Evaluate 1000 cases

    cases = [create_fraud_case(row) for _, row in df.iterrows()]

    print("Initializing investigation service...")
    service = InvestigationService(use_llm_planner=False, evaluation_mode=True)

    print("Running batch evaluation...")
    results = run_batch(cases, service)

    print("Computing fraud detection metrics...")
    classification_metrics = compute_metrics(results)

    print("Computing system-level metrics...")
    system_metrics = compute_additional_metrics(results)

    print("\n==============================")
    print(" FRAUD DETECTION METRICS")
    print("==============================")
    for k, v in classification_metrics.items():
        print(f"{k}: {v}")

    print("\n==============================")
    print(" SYSTEM GOVERNANCE METRICS")
    print("==============================")
    for k, v in system_metrics.items():
        print(f"{k}: {v}")

    print("\nEvaluation Complete.")


if __name__ == "__main__":
    main()