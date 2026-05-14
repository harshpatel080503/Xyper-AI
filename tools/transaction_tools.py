import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.settings import FraudCase

def load_transactions(path: str):
    return pd.read_csv(path)

def create_fraud_case(row, dataset_type="paysim") -> FraudCase:
    """
    Creates a FraudCase object with mappings for different datasets.
    """
    if dataset_type == "paysim":
        return FraudCase(
            transaction_id=str(row.name),
            user_id=str(row.get("nameOrig", "unknown")),
            amount=float(row.get("amount", 0)),
            transaction_type=str(row.get("type", "unknown")),
            timestamp=int(row.get("step", 0)),
            origin_balance=float(row.get("oldbalanceOrg", 0)),
            destination_balance=float(row.get("newbalanceDest", 0)),
            is_flagged=bool(row.get("isFraud", False)),
            metadata=row.to_dict()
        )
    elif dataset_type == "creditcard":
        return FraudCase(
            transaction_id=str(row.name),
            user_id="unknown", # Credit Card dataset is anonymized
            amount=float(row.get("Amount", 0)),
            transaction_type="credit_card",
            timestamp=int(row.get("Time", 0)),
            origin_balance=0.0,
            destination_balance=0.0,
            is_flagged=bool(row.get("Class", False)),
            metadata=row.to_dict()
        )
    elif dataset_type == "banksim":
        return FraudCase(
            transaction_id=str(row.name),
            user_id=str(row.get("customer", "unknown")),
            amount=float(row.get("amount", 0)),
            transaction_type=str(row.get("category", "unknown")),
            timestamp=int(row.get("step", 0)),
            origin_balance=0.0,
            destination_balance=0.0,
            is_flagged=bool(row.get("fraud", False)),
            metadata=row.to_dict()
        )
    elif dataset_type == "ibm_aml":
        return FraudCase(
            transaction_id=str(row.name),
            user_id=str(row.get("Account", "unknown")),
            amount=float(row.get("Amount Received", 0)),
            transaction_type=str(row.get("Payment Method", "unknown")),
            timestamp=int(row.get("Timestamp", 0) if isinstance(row.get("Timestamp"), int) else 0),
            origin_balance=0.0,
            destination_balance=0.0,
            is_flagged=bool(row.get("Is Laundering", False)),
            metadata=row.to_dict()
        )
    else:
        # Generic fallback
        return FraudCase(
            transaction_id=str(row.name),
            user_id="unknown",
            amount=float(row.get("amount", row.get("Amount", 0))),
            transaction_type="unknown",
            timestamp=0,
            origin_balance=0.0,
            destination_balance=0.0,
            is_flagged=False,
            metadata=row.to_dict()
        )

def get_user_history(df: pd.DataFrame, user_id: str, dataset_type="paysim") -> pd.DataFrame:
    """
    Returns historical transactions for a given user.
    """
    col = "nameOrig"
    if dataset_type == "banksim": col = "customer"
    elif dataset_type == "ibm_aml": col = "Account"
    
    if col in df.columns:
        if df.index.name == col:
            # High-performance index lookup
            try:
                history = df.loc[[user_id]]
            except KeyError:
                history = pd.DataFrame()
        else:
            # Fallback for unindexed data
            history = df[df[col] == user_id]
    else:
        history = pd.DataFrame()

    if history.empty:
        return pd.DataFrame({"amount": [0.0]})
    return history