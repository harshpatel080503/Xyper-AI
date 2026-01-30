FORBIDDEN_ACTIONS = {
    "auto_block_user",
    "irreversible_decision",
    "delete_user_data"   
}

def enforce_guardrails(action_name: str):
    if action_name in FORBIDDEN_ACTIONS:
        raise RuntimeError(
            f"Guardrail violation: {action_name} is forbidden"
        )