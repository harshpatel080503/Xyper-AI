import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.settings import FraudCase

def load_transactions(path: str):
    return pd.read_csv(path)

def create_fraud_case(row) -> FraudCase:
    return FraudCase(
        transaction_id=str(row.name),
        user_id=row["nameOrig"],
        amount=row["amount"],
        transaction_type=row["type"],
        timestamp=row["step"],
        origin_balance=row["oldbalanceOrg"],
        destination_balance=row["newbalanceDest"],
        is_flagged=bool(row["isFraud"]),
        metadata={}
    )