
from agents.gen_agent import run_gen_ai_agent
from graph.state import AgentState

from services.send_email import send_email_draft
from services.send_whatsapp import send_low_confidence_alert


def ai_agent_node(state: AgentState) -> dict:
    """
    Run the OpenAI support agent and store its output.
    """

    # Use email_text for the actual email content.
    # Fallback supports the existing app.py input format.
    email_text = (
        state.get("email_text")
        or state.get("customer_email", "")
    )

    try:
        agent_output = run_gen_ai_agent(email_text)

    except Exception as e:
        print(f"[OpenAI Agent Error] {e}")

        return {
            "confidence_score": 0,
            "draft_reply": (
                "Unable to generate a reliable response. "
                "Please review manually."
            ),
            "retrieved_context": "",
            "status": "pending_review",
        }

    return {
        "confidence_score": agent_output.get(
            "confidence_score", 0
        ),
        "draft_reply": agent_output.get(
            "draft_reply", ""
        ),
        "retrieved_context": agent_output.get(
            "retrieved_context", ""
        ),
        "status": agent_output.get(
            "status", "pending_review"
        ),
    }


def send_whatsapp_node(state: AgentState) -> dict:
    """
    Send a WhatsApp escalation alert when confidence is below 7.

    The recipient of the WhatsApp message is configured
    separately in Make.com/Twilio.
    """

    score = state.get("confidence_score", 0)

    # Additional safety check
    if score >= 7:
        print(
            "[WhatsApp] Confidence is 7 or above. "
            "Skipping escalation."
        )
        return {"status": "pending_review"}

    # Use the actual customer sender email,
    # not the entire customer email body.
    customer_email = state.get("sender", "Unknown")

    sent = send_low_confidence_alert(
        customer_email=customer_email,
        confidence_score=score,
        draft_reply=state.get("draft_reply", ""),
        status="escalated",
    )

    if sent:
        print("[WhatsApp] Escalation notification triggered.")
    else:
        print(
            "[WhatsApp] Notification failed. "
            "Manual escalation is still required."
        )

    # Keep the case escalated even if notification fails.
    return {"status": "escalated"}


def send_email_node(state: AgentState) -> dict:
    """
    Create a Gmail draft for high-confidence AI responses.
    """

    draft_id = send_email_draft(
        customer_email=state.get("sender", ""),
        draft_reply=state.get("draft_reply", ""),
        subject=state.get("subject", ""),
    )

    if not draft_id:
        print("[Gmail] Draft creation failed.")

        return {"status": "escalated"}

    print(f"[Gmail] Draft created successfully: {draft_id}")

    return {
        "status": "pending_review",
        "draft_id": draft_id,
    }
