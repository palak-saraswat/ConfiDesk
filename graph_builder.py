from langgraph.graph import StateGraph, START, END
from graph.state import AgentState
from graph.nodes import ai_agent_node, send_whatsapp_node, send_email_node

builder = StateGraph(AgentState)

builder.add_node("ai_agent", ai_agent_node)
builder.add_node("send_whatsapp", send_whatsapp_node)
builder.add_node("send_email", send_email_node)

builder.add_edge(START, "ai_agent")

def confidence_router(state: AgentState):
    score = state.get("confidence_score", 0)
    if score < 7:
        return "send_whatsapp"
    return "send_email"

builder.add_conditional_edges(
    "ai_agent",
    confidence_router,
    {
        "send_whatsapp": "send_whatsapp",
        "send_email": "send_email"
    }
)

builder.add_edge("send_whatsapp", END)
builder.add_edge("send_email", END)

graph = builder.compile()