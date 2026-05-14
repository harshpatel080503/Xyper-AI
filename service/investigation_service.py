import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph.investigation_graph import fraud_investigation_graph
from memory.memory_manager import MemoryManager
from configs.goal import InvestigationGoal
from storage.investigation_store import InvestigationStore
from memory.checkpointer import FileCheckpointer

class InvestigationService:
    def __init__(self, checkpointer=None, use_llm_planner=False, evaluation_mode=False):
        self.memory = MemoryManager()
        self.evaluation_mode = evaluation_mode
        # Avoid heavy checkpointing in evaluation mode to save memory/disk
        self.checkpointer = checkpointer or (FileCheckpointer() if not evaluation_mode else None)
        self.use_llm_planner = use_llm_planner

    def investigate(self, fraud_case, historical_data=None):
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
            "use_llm_planner": self.use_llm_planner,
            "evaluation_mode": self.evaluation_mode,
            "checkpointer": self.checkpointer,
            "historical_data": historical_data
        }   


        print(f"DEBUG: Starting graph invocation for {fraud_case.transaction_id}...")
        result = fraud_investigation_graph.invoke(initial_state)

        return result["final_report"]