"""
Real backend test – invokes the full LangGraph graph with a sample email
and creates a Gmail draft with the result.
"""
import os
from dotenv import load_dotenv
from graph_builder import graph
# Import your email service
from services.send_email import send_email_draft

load_dotenv()

# A sample customer email
test_email = (
    "Subject: Flight Tickets\n\n"
    "what is price for goa flight tickets right now?"
)

print("=" * 60)
print("🚀 Running the complete backend pipeline...")
print("=" * 60)

initial_state = {"customer_email": test_email}

try:
    # 1. Run the AI pipeline
    final_state = graph.invoke(initial_state)

    print("\n✅ Pipeline completed successfully!\n")
    print(f"📊 Confidence score : {final_state.get('confidence_score', 'N/A')} / 10")
    print(f"🏷️  Final status     : {final_state.get('status', 'N/A')}")
    
    ai_reply = final_state.get('draft_reply', '')
    print(f"📧 AI draft reply (first 300 chars):\n{ai_reply[:300]}...")

    # 2. Trigger Gmail draft creation based on the AI output
    if final_state.get("status") == "escalated":
        print("\n⚠️  Low confidence → WhatsApp alert triggered.")
    elif final_state.get("status") in ["pending_review", "approved"]:
        # Use the customer's email from the input if available, or a placeholder
        customer_email = "customer@example.com" 
        
        success = send_email_draft(customer_email, ai_reply)
        
        if success:
            print(f"\n📬 Success: New draft created in Gmail with the AI response!")
        else:
            print(f"\n❌ Error: Failed to create Gmail draft.")
    else:
        print(f"\n❓ Unexpected status: {final_state.get('status')}")

except Exception as e:
    print(f"\n❌ Pipeline failed with error: {e}")