from enum import Enum

class Permission(str, Enum):
    READ_DB = "read_db"
    WRITE_DB = "write_db"
    CALL_EXTERNAL_API = "call_external_api"
    GENERATE_REPORT = "generate_report"
    REQUEST_HUMAN = "request_human"

AGENT_PERMISSIONS  = {
    "planner_agent": {Permission.REQUEST_HUMAN},
    "transaction_agent": {Permission.READ_DB},
    "user_behavior_agent": {Permission.READ_DB},
    "risk_agent": {Permission.CALL_EXTERNAL_API},
    "report_agent": {Permission.GENERATE_REPORT},
}