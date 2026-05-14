import sys
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import json
from tqdm import tqdm

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.transaction_tools import create_fraud_case
from service.investigation_service import InvestigationService
from evaluation.metrics import compute_metrics

def run_dataset_eval(d_name, d_path, sample_size=600):
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    abs_path = os.path.join(PROJECT_ROOT, d_path)
    
    print(f"\n--- RUNNING EXPERIMENT: {d_name.upper()} ---")
    print(f"Targeting {sample_size} cases on Ollama Cloud...")

    if not os.path.exists(abs_path):
        print(f"Error: Data not found at {abs_path}")
        return

    df_full = pd.read_csv(abs_path)
    
    # Indexing for performance
    id_col = "nameOrig"
    if d_name == "banksim": id_col = "customer"
    elif d_name == "ibm_aml": id_col = "Account"
    
    if id_col in df_full.columns:
        df_full.set_index(id_col, drop=False, inplace=True)
        df_full.sort_index(inplace=True)

    fraud_col = "isFraud"
    if d_name == "creditcard": fraud_col = "Class"
    elif d_name == "banksim": fraud_col = "fraud"

    # Stratified Sampling (50/50 split for balanced evaluation)
    fraud_pool = df_full[df_full[fraud_col] == 1]
    legit_pool = df_full[df_full[fraud_col] == 0]
    
    s_fraud = min(len(fraud_pool), sample_size // 2)
    s_legit = sample_size - s_fraud
    
    test_df = pd.concat([
        fraud_pool.sample(s_fraud, random_state=42),
        legit_pool.sample(s_legit, random_state=42)
    ]).sample(frac=1, random_state=42)
    
    test_cases = [create_fraud_case(row, dataset_type=d_name) for _, row in test_df.iterrows()]
    
    service = InvestigationService(evaluation_mode=True)
    results = []
    
    for case in tqdm(test_cases, desc=f"{d_name} Eval"):
        try:
            report = service.investigate(case, historical_data=df_full)
            case_is_fraud = 1 if case.is_flagged else 0
            results.append({
                "transaction_id": case.transaction_id,
                "is_fraud": case_is_fraud,
                "predicted_fraud": 1 if report.get("decision") == "DECLINED" else 0,
                "confidence": report.get("confidence", 0.0),
                "governance_score": report.get("governance_score", 0.8),
                "logic_validation": report.get("logic_validation", "valid")
            })
        except Exception as e:
            print(f"Error on case {case.transaction_id}: {e}")

    # Store results
    os.makedirs("evaluation/results", exist_ok=True)
    out_path = f"evaluation/results/{d_name}_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"\n{d_name.upper()} evaluation complete. Results saved to {out_path}")

if __name__ == "__main__":
    run_dataset_eval("paysim", "data/raw/Paysim/paysim.csv")
