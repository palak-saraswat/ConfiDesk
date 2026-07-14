from typing import TypedDict, Optional

class AgentState(TypedDict):
    customer_email: str      
    draft_reply: Optional[str]
    confidence_score: int     # Score out of 10 determined by the agent
    status: str               # "pending_review", "approved", or "escalated"