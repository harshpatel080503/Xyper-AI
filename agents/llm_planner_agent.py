import json
import re

class LLMPlannerAgent:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = """
You are an autonomous fraud investigation planner.

GOAL:
{goal}

PAST CASES:
{past_cases}

BUDGET:
{budget}

AVAILABLE TOOLS:
transaction, user, risk

RULES:
- Output ONLY a JSON list
- No markdown
- No explanations

Valid example:
["transaction", "user", "risk"]
"""

    def _extract_json_array(self, text: str):
        """
        Extract first JSON array from LLM output.
        """
        # Remove markdown fences
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL).strip()

        # Find first JSON array
        match = re.search(r"\[[\s\S]*?\]", text)
        if not match:
            raise ValueError("No JSON array found in LLM output")

        return match.group(0)

    def plan(self, goal, past_cases, budget):
        response = self.llm.invoke(
            self.prompt.format(
                goal=goal.objective,
                past_cases=past_cases,
                budget=budget
            )
        )

        raw = response.content.strip()

        try:
            json_text = self._extract_json_array(raw)
            plan = json.loads(json_text)

            if not isinstance(plan, list):
                raise ValueError("Plan is not a list")

            return plan

        except Exception as e:
            # 🔒 SAFE FALLBACK (never crash system)
            return self._fallback_plan(goal)

    def _fallback_plan(self, goal):
        """
        Deterministic fallback when LLM misbehaves.
        """
        plan = ["transaction", "user"]

        if "risk" in goal.objective.lower():
            plan.append("risk")

        return plan







# import json
# import re

# class LLMPlannerAgent:
#     def __init__(self, llm):
#         if llm is None:
#             raise ValueError("LLMPlannerAgent requires a valid LLM")
#         self.llm = llm

#     def plan(self, goal, past_cases, budget):
#         prompt = f"""
# You are an autonomous fraud investigation planner.

# GOAL:
# {goal.objective}

# SIMILAR PAST CASES:
# {past_cases}

# BUDGET CONSTRAINTS:
# {budget}

# Do not exceed remaining_calls.

# AVAILABLE TOOLS:
# transaction, user, risk

# Return ONLY a JSON list of steps.
# Example:
# ["transaction", "user", "risk"]
# """

#         response = self.llm.invoke(prompt)

#         raw = response.content.strip()

#         try:
#             plan = json.loads(raw)
#         except Exception:
#             raise ValueError(
#                 f"Planner returned invalid JSON plan: {raw}"
#             )

#         if not isinstance(plan, list):
#             raise ValueError(
#                 f"Planner output is not a list: {plan}"
#             )

#         return plan