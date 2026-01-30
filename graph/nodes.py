import logging
import json
import sys
import os
import pandas as pd
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.planner_agent import PlannerAgent
from agents.transaction_agent import TransactionAgent
from agents.user_behavior_agent import UserBehaviorAgent
from agents.risk_agent import RiskAgent
from agents.critic_agent import CriticAgent
from agents.report_agent import ReportAgent
from langchain_openai import ChatOpenAI
from agents.llm_planner_agent import LLMPlannerAgent
from control_plane.policies import PolicyEngine
from control_plane.human_gate import human_review_required
from agents.rationale_llm_agent import RationaleLLM
from agents.prosecutor_agent import ProsecutorAgent
from agents.defender_agent import DefenderAgent

llm = ChatOpenAI(
    model="openai/gpt-oss-120b",
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)

planner = LLMPlannerAgent(llm=llm)
rationale_llm = RationaleLLM()
transaction_agent = TransactionAgent()
user_agent = UserBehaviorAgent()
risk_agent = RiskAgent()
critic_agent = CriticAgent()
report_agent = ReportAgent()
prosecutor = ProsecutorAgent()
defender = DefenderAgent()
policy_engine = PolicyEngine()

def enforce_step_limit(state):
    state["steps_taken"] += 1

    if state["steps_taken"] >= state["max_steps"]:
        return {
            "decision": human_review_required("Max steps exceeded"),
            "confidence": 0.0,
            "rationale": "Execution terminated due to safety step limit"
        }
    return None

logger = logging.getLogger("fraud_agent")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)

def planner_node(state):
    safety = enforce_step_limit(state)
    if safety:
        return safety
    observations = state.get("observations", [])
    if state.get("planned"):
        return {}

    goal = state["goal"]

    query = (
        f"amount {state['fraud_case'].amount} "
        f"type {state['fraud_case'].transaction_type}"
    )

    past_cases = state["memory"].recall_similar(query)
    
    budget = {
        "max_external_calls": 3,
        "remaining_calls": max(
            0, 3 - sum(
                1 for o in observations
                if o.get("tool") == "risk_agent"
            )
        )
    }

    plan = planner.plan(
        goal=goal,
        past_cases=past_cases,
        budget=budget
    )

    feedback = state.get("critic_feedback")

    if feedback:
        # If critic says confidence is low, expand plan
        if feedback.get("low_confidence") and "risk" not in plan:
            plan.append("risk")
        
        # If signals conflict, add user re-check
        if feedback.get("signal_conflict") and "user" not in plan:
            plan.append("user")

    state["_trace"] = {
        "planner_model": "gpt-oss-120b",
        "prompt_version": "v1.2",
        "plan": plan
    }

    return {
        "plan": plan,
        "planned": True
    }

def replanner_node(state):
    safety = enforce_step_limit(state)
    if safety:
        return safety

    if not state.get("replan"):
        return {}

    old_plan = state.get("plan", [])

    mutated_plan = []

    if "risk" not in old_plan:
        mutated_plan.append("risk")

    if "user" not in old_plan:
        mutated_plan.append("user")

    mutated_plan.extend(old_plan)

    return {
        "plan": mutated_plan,
        "planned": False,
        "_trace": {
            **state.get("_trace", {}),
            "replan_reason": state.get("replan_reason"),
            "mutated_plan": mutated_plan
        }
    }

def transaction_node(state):
    safety = enforce_step_limit(state)
    if safety:
        return safety
    result = transaction_agent.analyze(state["fraud_case"])
    return {
        "evidence": [result],
        "observations": [{
            "tool": "transaction_agent",
            "status": "success",
            "confidence_penalty": 0.0
        }]
    }

def user_node(state):
    safety = enforce_step_limit(state)
    if safety:
        return safety
    fake_history = pd.DataFrame({"amount": [100, 200, 150, 180]})
    result = user_agent.analyze(state["fraud_case"], fake_history)

    return {
        "evidence": [result],
        "observations": [{
            "tool": "user_behavior_agent",
            "status": "success",
            "confidence_penalty": 0.0
        }]
    }

def risk_node(state):
    safety = enforce_step_limit(state)
    if safety:
        return safety
    memory = state["memory"]

    try:
        cached_risk = memory.stm.get("geo_risk")
        if cached_risk:
            return {
                "evidence": [{"agent": "risk_agent", "geo_risk": cached_risk}],
                "observations": [{
                    "tool": "risk_agent",
                    "status": "success",
                    "fallback_used": True,
                    "confidence_penalty": 0.05
                }]
            }

        risk_score = risk_agent.analyze(state["fraud_case"])["geo_risk"]
        memory.stm.set("geo_risk", risk_score)

        return {
            "evidence": [{"agent": "risk_agent", "geo_risk": risk_score}],
            "observations": [{
                "tool": "risk_agent",
                "status": "success",
                "fallback_used": False,
                "confidence_penalty": 0.0
            }]
        }

    except Exception:
        return {
            "observations": [{
                "tool": "risk_agent",
                "status": "failed",
                "fallback_used": True,
                "confidence_penalty": 0.15
            }]
        }

def critic_node(state):
    # -----------------------------
    # Safety: step limit
    # -----------------------------
    safety = enforce_step_limit(state)
    if safety:
        return safety

    evidence = state["evidence"]
    observations = state.get("observations", [])
    memory = state["memory"]

    # -----------------------------
    # Extract signals
    # -----------------------------
    transaction_severity = 0.0
    user_deviation = 0.0
    geo_risk = 0.0

    for e in evidence:
        if e["agent"] == "transaction_agent":
            transaction_severity = e.get("severity", 0.0)
        elif e["agent"] == "user_behavior_agent":
            user_deviation = e.get("deviation", 0.0)
        elif e["agent"] == "risk_agent":
            geo_risk = e.get("geo_risk", 0.0)

    # -----------------------------
    # Evidence quality score
    # -----------------------------
    evidence_score = (
        0.4 * transaction_severity +
        0.3 * user_deviation +
        0.3 * geo_risk
    )

    # -----------------------------
    # Base confidence
    # -----------------------------
    confidence = 1.0

    for obs in observations:
        confidence -= obs.get("confidence_penalty", 0.0)

    # Historical consistency boost
    query = (
        f"amount {state['fraud_case'].amount} "
        f"type {state['fraud_case'].transaction_type}"
    )

    similar_cases = memory.recall_similar(query)
    if similar_cases:
        confidence += 0.05

    # Penalize strong evidence
    confidence -= 0.3 * evidence_score

    # Disagreement penalty
    signal_variance = max(
        abs(transaction_severity - geo_risk),
        abs(user_deviation - geo_risk)
    )
    confidence -= 0.2 * signal_variance

    # Tool failure penalty
    if any(o["status"] == "failed" for o in observations):
        confidence -= 0.15

    confidence = max(0.05, min(confidence, 0.95))

    # -----------------------------
    # Multi-agent debate
    # -----------------------------
    prosecution_args = prosecutor.argue(evidence, confidence)
    defense_args = defender.argue(evidence, confidence)

    prosecution_pressure = len(prosecution_args)
    defense_pressure = len(defense_args)

    # Debate-adjusted confidence
    confidence += 0.05 * (defense_pressure - prosecution_pressure)
    confidence = max(0.05, min(confidence, 0.95))

    # -----------------------------
    # Explainable rationale
    # -----------------------------
    rationale = (
        f"Defense: {', '.join(defense_args) if defense_args else 'none'} | "
        f"Prosecution: {', '.join(prosecution_args) if prosecution_args else 'none'}"
    )

    # -----------------------------
    # Policy validation
    # -----------------------------
    context = {
        "external_calls": len(observations),
        "confidence": confidence
    }

    allowed, reason = policy_engine.validate(context)

    if state.get("checkpointer"):
        state["checkpointer"].save(state)

    # -----------------------------
    # Escalation path
    # -----------------------------
    if not allowed or confidence < 0.6:
        decision = human_review_required(reason)

        logger.info(json.dumps({
            "event": "decision_made",
            "transaction_id": state["fraud_case"].transaction_id,
            "decision": decision["status"],
            "confidence": confidence,
            "evidence_score": evidence_score,
            "steps_taken": state["steps_taken"]
        }))

        critic_feedback = {
            "low_confidence": confidence < 0.7,
            "missing_risk_check": geo_risk == 0.0,
            "signal_conflict": signal_variance > 0.3,
            "strong_prosecution": prosecution_pressure > defense_pressure
        }

        return {
            "decision": decision,
            "confidence": confidence,
            "evidence_score": evidence_score,
            "rationale": rationale,
            "critic_feedback": critic_feedback,
            "replan": True,
            "replan_reason": "low_confidence_or_policy",
            "_trace": {
                "node": "critic",
                "planner_model": state.get("_trace", {}).get("planner_model"),
                "prompt_version": state.get("_trace", {}).get("prompt_version"),
                "plan": state.get("_trace", {}).get("plan"),
                "confidence": confidence,
                "evidence_score": evidence_score,
                "policy_reason": reason,
                "defense_arguments": defense_args,
                "prosecution_arguments": prosecution_args
            }
        }

    # -----------------------------
    # Approval path
    # -----------------------------
    logger.info(json.dumps({
        "event": "decision_made",
        "transaction_id": state["fraud_case"].transaction_id,
        "decision": "APPROVED",
        "confidence": confidence,
        "evidence_score": evidence_score,
        "steps_taken": state["steps_taken"]
    }))

    critic_feedback = {
        "low_confidence": confidence < 0.7,
        "missing_risk_check": geo_risk == 0.0,
        "signal_conflict": signal_variance > 0.3,
        "strong_prosecution": prosecution_pressure > defense_pressure
    }

    return {
        "decision": "APPROVED",
        "confidence": confidence,
        "evidence_score": evidence_score,
        "rationale": rationale,
        "critic_feedback": critic_feedback,
        "replan": False
    }

def report_node(state):
    safety = enforce_step_limit(state)
    if safety:
        return safety
    
    report = report_agent.generate(
        state["fraud_case"],
        state["evidence"],
        state["decision"]
    )

    if "rationale" in state and "confidence" in state:
        try:
            report["human_rationale"] = rationale_llm.rewrite(
                state["rationale"],
                state["confidence"]
            )
        except Exception:
            # Fallback to rule-based rationale
            report["human_rationale"] = state["rationale"]

    summary = f"""
    Transaction {report['transaction_id']}
    Decision: {report['decision']}
    Evidence count: {len(report['evidence'])}
    """

    if (
        state.get("confidence", 0) > 0.75 and
        (
            state["decision"] == "APPROVED" or
            state["decision"].get("status") == "HUMAN_REVIEW"
            )
        ):
            report["stored_at"] = datetime.datetime.utcnow().isoformat()
            state["memory"].remember_case(summary, metadata=report)

    if "stored_at" in report:
        logger.info(json.dumps({
            "event": "memory_written",
            "transaction_id": report["transaction_id"],
            "stored_at": report["stored_at"],
            "event": "rationale_check",
            "has_rationale": "rationale" in state,
            "rationale": state.get("rationale")
        }))

    if state.get("checkpointer"):
        state["checkpointer"].save(state)
    return {"final_report": report}








# def critic_node(state):
#     safety = enforce_step_limit(state)
#     if safety:
#         return safety
#     evidence = state["evidence"]
#     observations = state.get("observations", [])
#     memory = state["memory"]

#     transaction_severity = 0.0
#     user_deviation = 0.0
#     geo_risk = 0.0

#     for e in evidence:
#         if e["agent"] == "transaction_agent":
#             transaction_severity = e.get("severity", 0.0)
#         elif e["agent"] == "user_behavior_agent":
#             user_deviation = e.get("deviation", 0.0)
#         elif e["agent"] == "risk_agent":
#             geo_risk = e.get("geo_risk", 0.0)

#     evidence_score = (
#         0.4 * transaction_severity +
#         0.3 * user_deviation +
#         0.3 * geo_risk
#     )

#     rationale_parts = []

#     if transaction_severity > 0:
#         rationale_parts.append("transaction anomalies detected")

#     if user_deviation > 0:
#         rationale_parts.append("user behavior deviation observed")

#     if geo_risk < 0.4:
#         rationale_parts.append("geo risk is low")
    
#     confidence = 1.0

#     for obs in observations:
#         confidence -= obs.get("confidence_penalty", 0)

#     query = (
#         f"amount {state['fraud_case'].amount} "
#         f"type {state['fraud_case'].transaction_type}"
#     )

#     similar_cases = memory.recall_similar(query)

#     if similar_cases:
#         confidence += 0.05

#     confidence -= 0.3 * evidence_score
#     signal_variance = max(
#         abs(transaction_severity - geo_risk),
#         abs(user_deviation - geo_risk)
#     )

#     confidence -= 0.2 * signal_variance

#     if any(o["status"] == "failed" for o in observations):
#         confidence -= 0.15

#     confidence = max(0.05, min(confidence, 0.95))
    
#     prosecution_args = prosecutor.argue(evidence, confidence)
#     defense_args = defender.argue(evidence, confidence)

#     # Debate pressure
#     prosecution_pressure = len(prosecution_args)
#     defense_pressure = len(defense_args)

#     # Adjust confidence via debate
#     confidence += 0.05 * (defense_pressure - prosecution_pressure)
#     confidence = max(0.05, min(confidence, 0.95))

#     rationale = (
#         f"Defense: {', '.join(defense_args) if defense_args else 'none'} | "
#         f"Prosecution: {', '.join(prosecution_args) if prosecution_args else 'none'}"
#     )

#     context = {
#         "external_calls": len(observations),
#         "confidence": confidence
#     }

#     allowed, reason = policy_engine.validate(context)
#     if state.get("checkpointer"):
#         state["checkpointer"].save(state)

#     if not allowed or confidence < 0.6:

#         decision = human_review_required(reason)
#         logger.info(json.dumps({
#             "event": "decision_made",
#             "transaction_id": state["fraud_case"].transaction_id,
#             "decision": decision["status"],
#             "confidence": confidence,
#             "evidence_score": evidence_score,
#             "steps_taken": state["steps_taken"]
#         }))

#         critic_feedback = {
#             "low_confidence": confidence < 0.7,
#             "missing_risk_check": geo_risk == 0.0,
#             "signal_conflict": signal_variance > 0.3,
#             "strong_prosecution": prosecution_pressure > defense_pressure
#         }
        
#         return {
#             "decision": human_review_required(reason),
#             "confidence": confidence,
#             "evidence_score": evidence_score,
#             "rationale": rationale,
#             "critic_feedback": critic_feedback,
#             "replan": True,
#             "replan_reason": "low_confidence_or_failure",
#             "_trace": {
#                 "node": "critic",
#                 "planner_model": state.get("_trace", {}).get("planner_model"),
#                 "prompt_version": state.get("_trace", {}).get("prompt_version"),
#                 "plan": state.get("_trace", {}).get("plan"),
#                 "confidence": confidence,
#                 "evidence_score": evidence_score,
#                 "policy_reason": reason,
#                 "defense_arguments": defense_args,
#                 "prosecution_arguments": prosecution_args
#             }
#         }

#     decision = "APPROVED"

#     logger.info(json.dumps({
#             "event": "decision_made",
#             "transaction_id": state["fraud_case"].transaction_id,
#             "decision": decision,
#             "confidence": confidence,
#             "evidence_score": evidence_score,
#             "steps_taken": state["steps_taken"]
#         }))
    
#     critic_feedback = {
#         "low_confidence": confidence < 0.7,
#         "missing_risk_check": geo_risk == 0.0,
#         "signal_conflict": signal_variance > 0.3,
#         "strong_prosecution": prosecution_pressure > defense_pressure
#     }

#     return {
#         "decision": "APPROVED",
#         "confidence": confidence,
#         "evidence_score": evidence_score,
#         "rationale": rationale,
#         "critic_feedback": critic_feedback,
#         "replan": False
#     }