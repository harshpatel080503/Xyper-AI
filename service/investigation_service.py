import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.investigation_graph import fraud_investigation_graph
from memory.memory_manager import MemoryManager
from configs.goal import InvestigationGoal
from storage.investigation_store import InvestigationStore
from memory.checkpointer import FileCheckpointer

class InvestigationService:
    def __init__(self, checkpointer=None):
        self.memory = MemoryManager()
        self.checkpointer = checkpointer or FileCheckpointer()

    def investigate(self, fraud_case):
        initial_state = {
            "fraud_case": fraud_case,
            "goal": InvestigationGoal(
                objective="Investigate suspicious transaction",
                constraints=[],
                success_criteria="Correct fraud decision"
            ),

            # Planner state
            "plan": [],
            "planned": False,

            # Evidence & tools
            "evidence": [],
            "observations": [],

            # Decision outputs
            "decision": "",
            "confidence": 0.0,
            "rationale": "",
            "critic_feedback": {},
            "replan": False,

            # Tracing / audit
            "_trace": {},

            # Final output
            "final_report": {},

            # Infra
            "memory": self.memory,
            "max_steps": 6,
            "steps_taken": 0,
            "checkpointer": self.checkpointer
        }   

        result = fraud_investigation_graph.invoke(initial_state)

        return result["final_report"]