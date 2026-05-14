import json
import os
import pandas as pd
from evaluation.metrics import compute_metrics

def aggregate():
    results_dir = "evaluation/results"
    all_results = []
    
    if not os.path.exists(results_dir):
        print(f"No results found in {results_dir}")
        return

    print(f"--- AGGREGATING IEEE EXPERIMENTATION RESULTS ---")
    
    for filename in os.listdir(results_dir):
        if filename.endswith(".json") and "final_" not in filename:
            with open(os.path.join(results_dir, filename), "r") as f:
                dataset_results = json.load(f)
                all_results.extend(dataset_results)
                print(f"Loaded {len(dataset_results)} cases from {filename}")

    if not all_results:
        print("No cases loaded.")
        return

    metrics = compute_metrics(all_results)
    
    print("\n" + "="*50)
    print("FINAL IEEE AGGREGATED METRICS")
    print("="*50)
    print(f"Total Transactions: {len(all_results)}")
    print(f"Precision: {metrics['performance']['precision']:.4f}")
    print(f"Recall:    {metrics['performance']['recall']:.4f}")
    print(f"F1-Score:  {metrics['performance']['f1_score']:.4f}")
    print(f"AUC-ROC:   {metrics['performance']['auc_roc']:.4f}")
    print("-"*50)
    print(f"Governance Score: {metrics['governance']['avg_governance_score']:.4f}")
    print(f"Logical Integrity: {metrics['governance']['logical_integrity']:.2f}%")
    print("="*50)

    with open("evaluation/results/final_ieee_aggregated.json", "w") as f:
        json.dump(metrics, f, indent=4)
    print("\nFinal report saved to evaluation/results/final_ieee_aggregated.json")

if __name__ == "__main__":
    aggregate()
