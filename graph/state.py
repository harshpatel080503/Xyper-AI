import os
import sys
from typing import TypedDict, List, Dict, Any
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configs.settings import FraudCase
from typing_extensions import Annotated
from memory.memory_manager import MemoryManager
from configs.goal import InvestigationGoal

def evidence_reducer(existing, new):
    seen = set()
    merged = []

    for item in existing + new:
        key = (item.get("agent"), str(item))
        if key not in seen:
            seen.add(key)
            merged.append(item)

    return merged

class InvestigationState(TypedDict):
    fraud_case: FraudCase
    goal: InvestigationGoal
    plan: list
    planned: bool
    evidence: Annotated[list, evidence_reducer]
    observations: Annotated[list, evidence_reducer]
    checkpointer: any
    confidence: float
    rationale: str
    evidence_score: float
    critic_feedback: dict
    decision: any
    final_report: dict
    memory: MemoryManager
    max_steps: int
    steps_taken: int