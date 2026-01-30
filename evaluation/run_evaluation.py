import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
from tqdm import tqdm
from tools.transaction_tools import load_transactions, create_fraud_case
from service.investigation_service import InvestigationService
from evaluation.batch_runner import run_batch
from evaluation.metrics import compute_metrics

df = load_transactions("E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv")

cases = [
    create_fraud_case(df.iloc[i])
    for i in range(1000)
]

service = InvestigationService()

results = run_batch(cases, service)

metrics = compute_metrics(results)

print("\n===== FRAUD SYSTEM METRICS =====")
for k, v in metrics.items():
    print(f"{k}: {v}")










# import sys
# import os

# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.insert(0, PROJECT_ROOT)

# import json
# import pandas as pd

# from evaluation.batch_runner import run_batch
# from evaluation.metrics import compute_metrics
# from evaluation.configs import EVAL_CONFIG

# from tools.transaction_tools import load_transactions, create_fraud_case
# from service.investigation_service import InvestigationService

# def main():
#     service = InvestigationService()

#     df = load_transactions(
#         "E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv"
#     ).head(EVAL_CONFIG["max_cases"])

#     cases = [create_fraud_case(row) for _, row in df.iterrows()]

#     results = run_batch(cases, service)
#     metrics = compute_metrics(results)

#     print("\n===== EVALUATION METRICS =====")
#     for k, v in metrics.items():
#         print(f"{k}: {v}")

#     with open(EVAL_CONFIG["store_results_path"], "w") as f:
#         json.dump({
#             "metrics": metrics,
#             "results": results
#         }, f, indent=2)

# if __name__ == "__main__":
#     main()