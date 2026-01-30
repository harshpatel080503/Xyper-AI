from langchain_community.callbacks.tracers import LangChainTracer
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---- External tools ----
from tools.transaction_tools import load_transactions, create_fraud_case

# ---- Service boundary (NEW) ----
from service.investigation_service import InvestigationService

# ---- Optional (future use) ----
from feedback.feedback_store import FeedbackStore

# ---- LangSmith Tracing ----
tracer = LangChainTracer(project_name="fraud-agentic-system")

config = {
    "callbacks": [tracer],
    "recursion_limit": 50
}

# ---- Load data ----
df = load_transactions(
    "E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv"
)
case = create_fraud_case(df.iloc[0])

# ---- Initialize service ----
service = InvestigationService()

# ---- Run investigation ----
report = service.investigate(case)

print("\n============ Final Investigation Report ============\n")
pprint(report)

# -------------------------------------------------
# FUTURE: Human-in-the-loop feedback (RLHF)
# When a human reviewer overrides the decision,
# call:
#
# feedback_store = FeedbackStore()
# feedback_store.record(
#     transaction_id=report["transaction_id"],
#     decision=report["decision"],
#     human_label="<HUMAN_DECISION>",
#     notes="<OPTIONAL_NOTES>"
# )
# -------------------------------------------------







# from langchain_community.callbacks.tracers import LangChainTracer
# from pprint import pprint
# from dotenv import load_dotenv
# load_dotenv()
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from graph.investigation_graph import fraud_investigation_graph
# from tools.transaction_tools import load_transactions, create_fraud_case
# from memory.memory_manager import MemoryManager
# from configs.goal import InvestigationGoal
# from memory.checkpointer import FileCheckpointer
# from feedback.feedback_store import FeedbackStore

# tracer = LangChainTracer(project_name="fraud-agentic-system")

# config = {
#     "callbacks": [tracer],
#     "recursion_limit": 50
# }

# goal = InvestigationGoal(
#     objective="Investigate suspicious transaction safely",
#     constraints=[
#         "Follow fraud policies",
#         "Limit external API usage",
#         "Escalate if confidence < 0.6"
#     ],
#     success_criteria="Approve or escalate with explanation"
# )

# memory = MemoryManager()
# checkpointer = FileCheckpointer()

# feedback_store = FeedbackStore()

# df = load_transactions("E:/Data Science Study/Project/Data Science/Autonomous Fraud Investigation Agentic AI System/data/raw/paysim.csv")
# case = create_fraud_case(df.iloc[0])

# initial_state = {
#     "fraud_case": case,
#     "goal": InvestigationGoal(
#         objective="Investigate suspicious transaction",
#         constraints=[],
#         success_criteria="Correct fraud decision"
#     ),
#     "plan": [],
#     "planned": False,
#     "evidence": [],
#     "decision": "",
#     "final_report": {},
#     "memory": memory,
#     "checkpointer": checkpointer
# }

# result = fraud_investigation_graph.invoke(initial_state, config=config)
# print("\n============Final Investigation Report==================\n")
# pprint(result["final_report"])


# # -------------------------------------------------
# # FUTURE: Human-in-the-loop feedback (RLHF)
# # When a human reviewer overrides the decision,
# # call:
# #
# # feedback_store.record(
# #     transaction_id=final_report["transaction_id"],
# #     decision=final_report["decision"],
# #     human_label="<HUMAN_DECISION>",
# #     notes="<OPTIONAL_NOTES>"
# # )
# # -------------------------------------------------