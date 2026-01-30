from pydantic import BaseModel
from typing import Dict, Any

class FraudCase(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    transaction_type: str
    timestamp: int
    origin_balance: float
    destination_balance: float
    is_flagged: bool
    metadata: Dict[str, Any] = {}
