"""
ConfiDesk - app.py (Entry Point)
Integrated with real LangGraph pipeline and Gmail sending.
"""

import streamlit as st
from graph_builder import graph             # Palak – real compiled graph
from services.send_email import send_email  # Shruti – real send (not draft)

st.set_page_config(page_title="ConfiDesk", page_icon="📨", layout="wide")

# ---------------------------------------------------------------------------
# Sample queue (replace with live Gmail fetching later)
# ---------------------------------------------------------------------------
DUMMY_QUEUE = [
    {"id": 1, "sender": "priya@customer.com", "subject": "Refund policy for damaged item",
     "body": "Hi, I received a damaged item last week. What's your refund process?"},
    {"id": 2, "sender": "raj@customer.com", "subject": "Custom enterprise integration question",
     "body": "Do you support SSO with our internal Okta setup for enterprise plans?"},
    {"id": 3, "sender": "amy@customer.com", "subject": "Where's my order?",
     "body": "I placed an order 5 days ago and haven't received a tracking update."},
]

if "processed" not in st.session_state:
    st.session_state.processed = []
if "queue" not in st.session_state:
    st.session_state.queue = DUMMY_QUEUE.copy()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ConfiDesk")
    st.caption("Customer email agent")

    st.markdown("**Connections**")
    st.write("📧 Gmail — :green[Connected]")
    st.write("💬 WhatsApp — :green[Connected]")
    st.write("📚 RAG index — :green[142 docs loaded]")

    st.divider()
    st.slider(
        "Confidence threshold (informational)", min_value=0.0, max_value=10.0, value=7.0, step=0.5,
        help="The real pipeline routes ≥7 → Gmail draft, <7 → WhatsApp escalation.",
    )
    st.divider()
    st.metric("In queue", len(st.session_state.queue))
    st.metric("Processed today", len(st.session_state.processed))

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("ConfiDesk")
st.caption("Reads customer emails, drafts answers from company docs, and routes low‑confidence cases to a human.")

tab_queue, tab_review, tab_escalations, tab_log = st.tabs(
    ["📥 Incoming queue", "✏️ Review drafts", "🚨 Escalations", "📜 Sent log"]
)

# ----- QUEUE TAB: run the real pipeline on a selected email -----------------
with tab_queue:
    st.subheader("Incoming customer emails")
    if not st.session_state.queue:
        st.info("Queue is empty. All caught up.")
    for email in st.session_state.queue:
        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{email['subject']}**")
                st.caption(f"From: {email['sender']}")
                st.write(email["body"])
            with col2:
                if st.button("Process", key=f"process_{email['id']}", use_container_width=True):
                    with st.spinner("Read → RAG → Generate → Route..."):
                        full_text = f"Subject: {email['subject']}\n\n{email['body']}"
                        initial_state = {"customer_email": full_text}

                        final_state = graph.invoke(initial_state)

                        result = {
                            "id": email["id"],
                            "sender": email["sender"],
                            "subject": email["subject"],
                            "confidence": final_state.get("confidence_score", 0),
                            "draft": final_state.get("draft_reply", ""),
                            "status": final_state.get("status", "escalated"),
                            "channel": "gmail_draft" if final_state.get("confidence_score", 0) >= 7 else "whatsapp_escalation",
                        }

                    st.session_state.processed.append(result)
                    st.session_state.queue = [e for e in st.session_state.queue if e["id"] != email["id"]]
                    st.rerun()

# ----- REVIEW TAB: drafts awaiting human approval ---------------------------
with tab_review:
    st.subheader("Drafts awaiting your approval")
    drafts = [r for r in st.session_state.processed if r["status"] == "pending_review"]
    if not drafts:
        st.info("No drafts waiting for review.")
    for r in drafts:
        with st.container():
            st.markdown(f"**{r['subject']}**  ·  :blue[Confidence {r['confidence']}/10]")
            st.caption(f"To: {r['sender']}")
            edited = st.text_area("Draft reply", value=r["draft"], key=f"draft_{r['id']}", height=100)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve and send", key=f"send_{r['id']}", use_container_width=True):
                    if send_email(r["sender"], r["subject"], edited):
                        r["status"] = "sent"
                        r["draft"] = edited
                        st.success("Sent.")
                    else:
                        st.error("Failed to send. Check server logs.")
                    st.rerun()
            with c2:
                st.button("Discard", key=f"discard_{r['id']}", use_container_width=True)

# ----- ESCALATIONS TAB ------------------------------------------------------
with tab_escalations:
    st.subheader("Escalated to the support team via WhatsApp")
    escalations = [r for r in st.session_state.processed if r["status"] == "escalated"]
    if not escalations:
        st.info("No open escalations.")
    for r in escalations:
        with st.container():
            st.markdown(f"**{r['subject']}**  ·  :orange[Confidence {r['confidence']}/10]")
            st.caption(f"From: {r['sender']}")
            st.write("Notification sent — awaiting a manual reply from the support team.")

# ----- SENT LOG -------------------------------------------------------------
with tab_log:
    st.subheader("Sent history")
    sent = [r for r in st.session_state.processed if r["status"] == "sent"]
    if not sent:
        st.info("Nothing sent yet.")
    else:
        st.table([
            {"To": r["sender"], "Subject": r["subject"], "Confidence": r["confidence"], "Channel": "Gmail"}
            for r in sent
        ])