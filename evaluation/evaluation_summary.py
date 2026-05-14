import pandas as pd
import numpy as np
import sys
import os
import time
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.transaction_tools import load_transactions, create_fraud_case
from service.investigation_service import InvestigationService

def run_evaluation(num_cases=10):
    print(f"🚀 Starting Evaluation on {num_cases} cases...")
    
    # Load dataset
    data_path = "E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv"
    df = load_transactions(data_path)
    
    # Select sample (mix of fraud and non-fraud if possible)
    fraud_cases = df[df["isFraud"] == 1].head(num_cases // 2)
    normal_cases = df[df["isFraud"] == 0].head(num_cases // 2)
    sample_df = pd.concat([fraud_cases, normal_cases]).sample(frac=1)
    
    service = InvestigationService(use_llm_planner=True)
    results = []
    
    start_time = time.time()
    
    for i, (_, row) in enumerate(sample_df.iterrows()):
        case = create_fraud_case(row)
        print(f"[{i+1}/{num_cases}] Investigating Transaction {case.transaction_id} (Amount: {case.amount})...")
        
        try:
            report = service.investigate(case, historical_data=df)
            results.append({
                "transaction_id": case.transaction_id,
                "amount": case.amount,
                "actual_label": row["isFraud"],
                "predicted_decision": report.get("decision"),
                "confidence": report.get("confidence", 0),
                "steps": report.get("steps_taken", 0)
            })
        except Exception as e:
            print(f"Error investigating {case.transaction_id}: {e}")

    end_time = time.time()
    
    # Analyze Results
    eval_df = pd.DataFrame(results)
    
    # Metrics
    metrics = {
        "total_cases": len(eval_df),
        "mean_confidence": eval_df["confidence"].mean(),
        "human_escalation_rate": (eval_df["predicted_decision"].apply(lambda x: isinstance(x, dict) and x.get("status") == "HUMAN_REVIEW")).mean(),
        "auto_approval_rate": (eval_df["predicted_decision"] == "APPROVED").mean(),
        "auto_decline_rate": (eval_df["predicted_decision"] == "DECLINED").mean(),
        "avg_processing_time": (end_time - start_time) / len(eval_df) if len(eval_df) > 0 else 0
    }
    
    print("\n" + "="*50)
    print("📊 EVALUATION SUMMARY")
    print("="*50)
    pprint(metrics)
    print("="*50)
    
    return metrics

if __name__ == "__main__":
    run_evaluation(num_cases=6)
