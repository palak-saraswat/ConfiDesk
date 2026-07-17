from typing import Optional, TypedDict


class AgentState(TypedDict):
    customer_email: str
    email_text: str

    intent: str
    extracted_query: str
    retrieved_context: str

    generated_response: str
    draft_reply: Optional[str]

    confidence_score: float
    status: str

    approved: bool
    escalated: bool

    final_response: Optional[str]