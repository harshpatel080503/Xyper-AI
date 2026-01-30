import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langgraph.graph import StateGraph, START, END
from graph.state import InvestigationState
from graph.nodes import (
    planner_node,
    transaction_node,
    user_node,
    risk_node,
    critic_node,
    report_node,
    replanner_node
)

graph = StateGraph(InvestigationState)

# ----------------------
# Register nodes
# ----------------------
graph.add_node("planner", planner_node)
graph.add_node("transaction", transaction_node)
graph.add_node("replanner", replanner_node)
graph.add_node("user", user_node)
graph.add_node("risk", risk_node)
graph.add_node("critic", critic_node)
graph.add_node("report", report_node)

# ----------------------
# Entry point
# ----------------------
graph.add_edge(START, "planner")

# ----------------------
# Planner-driven routing
# ----------------------
def route_from_plan(state):
    """
    Planner controls execution order.
    Pops next step from plan.
    """
    if not state["plan"]:
        return "critic"

    step = state["plan"].pop(0)
    return step


graph.add_conditional_edges(
    "planner",
    route_from_plan,
    {
        "transaction": "transaction",
        "user": "user",
        "risk": "risk",
        "critic": "critic",
    },
)

def route_after_critic(state):
    if state.get("replan"):
        return "replanner"
    return "report"

graph.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "replanner": "replanner",
        "report": "report"
    }
)


# ----------------------
# Loop back after each execution step
# ----------------------
graph.add_edge("transaction", "planner")
graph.add_edge("user", "planner")
graph.add_edge("risk", "planner")
graph.add_edge("replanner", "planner")

# ----------------------
# Final decision path
# ----------------------
graph.add_edge("critic", "report")
graph.add_edge("report", END)

# ----------------------
# Compile graph
# ----------------------
fraud_investigation_graph = graph.compile()








# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from langgraph.graph import StateGraph, START, END
# from graph.state import InvestigationState
# from graph.nodes import *

# graph = StateGraph(InvestigationState)

# graph.add_node("planner", planner_node)
# graph.add_node("transaction", transaction_node)
# graph.add_node("user", user_node)
# graph.add_node("risk", risk_node)
# graph.add_node("critic", critic_node)
# graph.add_node("report", report_node)

# graph.add_edge(START, "planner")
# graph.add_edge("planner", "transaction")
# graph.add_edge("planner", "user")

# def route_from_plan(state):
#     if not state["plan"]:
#         return "critic"
#     step = state["plan"].pop(0)
#     return step

# def route_risk(state):
#     return "risk" if "risk_intelligence" in state["plan"] else "critic"

# graph.add_conditional_edges(
#     "user",
#     route_risk,
#     {
#         "risk": "risk",
#         "critic": "critic"
#     }
# )

# graph.add_edge("risk", "critic")
# graph.add_edge("critic", "report")
# graph.add_edge("report", END)

# fraud_investigation_graph = graph.compile()

# # class InvestigationGraph:
# #     def run(self, fraud_case, agents):
# #         evidence = []

# #         for agent in agents:
# #             result = agent(fraud_case)
# #             evidence.append(result)

# #         return evidence