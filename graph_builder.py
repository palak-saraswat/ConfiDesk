from langgraph.graph import StateGraph, START, END

# Import the shared state dictionary structure
from graph.state import AgentState

# Import the Generative AI logic from your agent file
from agents.gen_agent import run_gen_ai_agent

# Import the node actions from your graph folder
from graph.nodes import (
    ai_agent_node,
    send_whatsapp_node,
    send_email_node
)

# Initialize the graph builder using your state definition
builder = StateGraph(AgentState)

# Add the operational nodes to the workflow layout
builder.add_node("ai_agent", ai_agent_node)
builder.add_node("send_whatsapp", send_whatsapp_node)
builder.add_node("send_email", send_email_node)

# Define the entry point connection
builder.add_edge(START, "ai_agent")

# Routing function to evaluate AI confidence score
def confidence_router(state: AgentState):
    score = state.get("confidence_score", 0)
    
    # If the generation has low confidence, route to the WhatsApp coordinator alert
    if score < 7:
        return "send_whatsapp"
    
    # If confidence is high, pass directly to email delivery
    return "send_email"

# Apply the conditional routing rules to the graph layout
builder.add_conditional_edges(
    "ai_agent",
    confidence_router,
    {
        "send_whatsapp": "send_whatsapp",
        "send_email": "send_email"
    }
)

# Complete the cycles by ending the execution loop at termination points
builder.add_edge("send_whatsapp", END)
builder.add_edge("send_email", END)

# Compile the workflow blueprint into an executable instance
graph = builder.compile()
