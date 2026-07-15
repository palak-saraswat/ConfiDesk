from agents.gen_agent import run_gen_ai_agent
from graph.state import AgentState

def ai_agent_node(state: AgentState):
    """
    LangGraph node that pulls the customer email from the state,
    passes it to the Gemini agent, and updates the state with the result.
    """
    # 1. Get the input from the state
    customer_email = state.get("customer_email", "")
    
    # 2. Run the Gemini generation agent function
    agent_output = run_gen_ai_agent(customer_email)
    
    # 3. Return the updates to merge into the workflow state
    return {
        "confidence_score": agent_output.get("confidence_score", 0),
        "draft_reply": agent_output.get("draft_reply", ""),
        "status": agent_output.get("status", "needs_review")
    }
    
from services.send_whatsapp import send_low_confidence_alert

def send_whatsapp_node(state):
    send_low_confidence_alert(
        customer_email=state.get("customer_email", ""),
        confidence_score=state.get("confidence_score", 0),
        draft_reply=state.get("draft_reply", ""),
        status=state.get("status", "escalated")
    )

    return {"status": "escalated"}

def send_email_node(state: AgentState):
    return {"status": "email_sent"}