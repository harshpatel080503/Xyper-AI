from pydantic import BaseModel

class InvestigationGoal(BaseModel):
    objective: str
    constraints: list
    success_criteria: str