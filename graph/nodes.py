from agents.gen_agent import run_gen_ai_agent
from graph.state import AgentState
from services.send_email import send_email_draft
from services.send_whatsapp import send_low_confidence_alert


def ai_agent_node(state: AgentState) -> dict:
    """
    LangGraph node that pulls the customer email from the state,
    passes it to the Gemini agent, and updates the state with the result.
    """
    customer_email = state.get("customer_email", "")

    try:
        agent_output = run_gen_ai_agent(customer_email)
    except Exception as e:
        # If the AI agent fails, treat it as low confidence and escalate
        print(f"Gemini agent failed: {e}")
        return {
            "confidence_score": agent_output.get("confidence_score", 0),
            "draft_reply": agent_output.get("draft_reply", ""),
            "status": agent_output.get("status", "pending_review"),
            "retrieved_context": agent_output.get("retrieved_context", ""),
        }


def send_whatsapp_node(state: AgentState) -> dict:
    """Send a WhatsApp alert for low-confidence replies."""
    send_low_confidence_alert(
        customer_email=state.get("customer_email", ""),
        confidence_score=state.get("confidence_score", 0),
        draft_reply=state.get("draft_reply", ""),
        status=state.get("status", "escalated"),
    )
    return {"status": "escalated"}


def send_email_node(state: AgentState) -> dict:
    """Create a Gmail draft for high-confidence replies."""
    send_email_draft(
        customer_email=state.get("customer_email", ""),
        draft_reply=state.get("draft_reply", ""),
    )
    return {"status": "pending_review"}   # draft waits for human approval