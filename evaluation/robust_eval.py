import sys
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy import stats
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from tools.transaction_tools import load_transactions, create_fraud_case
from service.investigation_service import InvestigationService
from evaluation.metrics import compute_metrics

def run_experiment(service, test_cases, dataset_type, df_full, desc="Agent"):
    results = []
    for case in tqdm(test_cases, desc=desc):
        try:
            # Set metadata for metric calculation
            case_is_fraud = 1 if case.is_flagged else 0
            
            # PASS THE INDEXED DATAFRAME HERE
            report = service.investigate(case, historical_data=df_full)
            results.append({
                "transaction_id": case.transaction_id,
                "is_fraud": case_is_fraud,
                "decision": report.get("decision"),
                "confidence": report.get("confidence", 0.5),
                "governance_score": report.get("governance_score", 1.0),
                "steps_taken": report.get("steps_taken", 0),
                "rationale": report.get("rationale", ""),
                "logic_validation": report.get("logic_validation", "valid")
            })
        except Exception as e:
            print(f"Error on case {case.transaction_id}: {e}")
    return results

def main():
    # 1. Configuration
    DATASETS = {
        "paysim": "data/raw/Paysim/paysim.csv",
        "creditcard": "data/raw/Credit Card Fraud/creditcard.csv",
        "banksim": "data/raw/BankSim/bs140513_032310.csv",
        "ibm_aml": "data/raw/IBM AML/HI-Small_Trans.csv"
    }
    
    NUM_ITERATIONS = 5
    # Full scale experimentation for IEEE GSCON
    SAMPLE_SIZE = 200 
    
    print(f"\n--- IEEE FULL-SCALE EXPERIMENTATION MODE ---")
    print(f"Sample size set to {SAMPLE_SIZE} per dataset across {NUM_ITERATIONS} iterations.\n")

    final_report_summary = {}

    service = InvestigationService(evaluation_mode=True)

    for d_name, d_path in DATASETS.items():
        abs_path = os.path.join(PROJECT_ROOT, d_path)
        if not os.path.exists(abs_path):
            print(f"Skipping {d_name}: File not found at {abs_path}")
            continue

        print(f"\n{'='*60}\nRUNNING EXPERIMENT ON DATASET: {d_name.upper()}\n{'='*60}")
        
        print(f"Loading and Indexing data from {abs_path}...")
        df_full = pd.read_csv(abs_path)
        
        # Performance Optimization: Index by User ID for fast history lookups
        id_col = "nameOrig"
        if d_name == "banksim": id_col = "customer"
        elif d_name == "ibm_aml": id_col = "Account"
        
        if id_col in df_full.columns:
            # We keep the column but also create a fast lookup index
            df_full.set_index(id_col, drop=False, inplace=True)
            df_full.sort_index(inplace=True)
            print(f"Successfully indexed {len(df_full)} rows by '{id_col}'.")
        
        # Fraud column mapping for stratified sampling
        fraud_col = "isFraud"
        if d_name == "creditcard": fraud_col = "Class"
        elif d_name == "banksim": fraud_col = "fraud"
        elif d_name == "ibm_aml": fraud_col = "Is Laundering"

        all_dataset_metrics = []

        for i in range(NUM_ITERATIONS):
            print(f"Iteration {i+1}/{NUM_ITERATIONS}...")
            
            # Stratified sampling
            fraud_pool = df_full[df_full[fraud_col] == 1]
            legit_pool = df_full[df_full[fraud_col] == 0]
            
            s_fraud = min(len(fraud_pool), SAMPLE_SIZE // 2)
            s_legit = min(len(legit_pool), SAMPLE_SIZE // 2)
            
            test_df = pd.concat([
                fraud_pool.sample(s_fraud, random_state=42+i),
                legit_pool.sample(s_legit, random_state=42+i)
            ]).sample(frac=1, random_state=42+i)
            
            test_cases = [create_fraud_case(row, dataset_type=d_name) for _, row in test_df.iterrows()]
            
            results = run_experiment(service, test_cases, d_name, df_full, desc=f"{d_name} Iter {i+1}")
            metrics = compute_metrics(results)
            all_dataset_metrics.append(metrics)
            
        # Aggregate results for this dataset
        dataset_summary = {"performance": {}, "governance": {}}
        
        p_metrics = ["precision", "recall", "f1_score", "auc_roc"]
        g_metrics = ["avg_steps_to_decision", "governance_compliance_score", "interpretability_proxy_score", "logical_integrity_rate"]
        
        for m in p_metrics:
            values = [it["performance"][m] for it in all_dataset_metrics]
            dataset_summary["performance"][m] = {"mean": np.mean(values), "std": np.std(values)}
            
        for m in g_metrics:
            values = [it["governance"][m] for it in all_dataset_metrics]
            dataset_summary["governance"][m] = {"mean": np.mean(values), "std": np.std(values)}

        final_report_summary[d_name] = dataset_summary

        # Print Dataset Summary
        print(f"\n--- {d_name.upper()} RESULTS SUMMARY ---")
        for m, s in dataset_summary["performance"].items():
            print(f"{m.upper():<25}: {s['mean']:.4f} \u00B1 {s['std']:.4f}")
        for m, s in dataset_summary["governance"].items():
            print(f"{m.upper():<25}: {s['mean']:.4f} \u00B1 {s['std']:.4f}")

    # 4. Final IEEE Results Table Generation
    print("\n" + "#"*60)
    print(" FINAL IEEE GSCON EXPERIMENTATION TABLE")
    print("#"*60)
    print(f"{'Dataset':<15} | {'F1-Score':<15} | {'AUC-ROC':<15} | {'Gov. Score':<15}")
    print("-" * 65)
    for d_name, summary in final_report_summary.items():
        f1 = summary["performance"]["f1_score"]
        auc = summary["performance"]["auc_roc"]
        gov = summary["governance"]["governance_compliance_score"]
        print(f"{d_name:<15} | {f1['mean']:.4f}\u00B1{f1['std']:.3f} | {auc['mean']:.4f}\u00B1{auc['std']:.3f} | {gov['mean']:.4f}\u00B1{gov['std']:.3f}")
    print("#"*60)

    # Save final aggregate
    with open(os.path.join(PROJECT_ROOT, "evaluation/final_ieee_results.json"), "w") as f:
        json.dump(final_report_summary, f, indent=2)

if __name__ == "__main__":
    main()
