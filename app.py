"""
ConfiDesk - app.py (Entry Point)
UI / UX SHELL ONLY.

This file lays out the interface and interaction flow. All "processing"
below is dummy/mocked so the app runs standalone for design review.
Each stub marked with # TODO(<name>) is where a teammate's real module
gets wired in later:

    from graph_builder import run_pipeline          # Palak
    from agents.gen_agent import generate_answer    # Soha
    from services.retriever import search_docs      # Soha
    from services.send_email import send_email      # Shruti
    from services.send_whatsapp import notify_team   # Vivanshi

Run with:  streamlit run app.py
"""

import streamlit as st
import time
import random

st.set_page_config(page_title="ConfiDesk", page_icon="📨", layout="wide")

# ---------------------------------------------------------------------------
# Dummy data (stand-ins for real queue / RAG / pipeline output)
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
    st.session_state.processed = []       # results after running the pipeline
if "queue" not in st.session_state:
    st.session_state.queue = DUMMY_QUEUE.copy()


def run_pipeline_dummy(email):
    """
    TODO(Palak/Soha): replace with real call, e.g.:
        result = run_pipeline(email)   # from graph_builder.py
    Returns a dict shaped like what the real graph will emit.
    """
    confidence = round(random.uniform(2, 10), 1)
    return {
        **email,
        "confidence": confidence,
        "draft": f"Hi {email['sender'].split('@')[0].title()}, thanks for reaching out. "
                 f"Based on our documentation, here's the answer to your question...",
        "channel": "gmail_draft" if confidence >= 7 else "whatsapp_escalation",
        "status": "pending_review" if confidence >= 7 else "escalated",
    }


# ---------------------------------------------------------------------------
# Sidebar — system status + controls
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### ConfiDesk")
    st.caption("Customer email agent")

    st.markdown("**Connections**")
    st.write("📧 Gmail — :green[Connected]")
    st.write("💬 WhatsApp — :green[Connected]")
    st.write("📚 RAG index — :green[142 docs loaded]")

    st.divider()

    threshold = st.slider(
        "Confidence threshold", min_value=0.0, max_value=10.0, value=7.0, step=0.5,
        help="≥ threshold → Gmail draft for human review. Below → WhatsApp escalation.",
    )

    st.divider()
    st.metric("In queue", len(st.session_state.queue))
    st.metric("Processed today", len(st.session_state.processed))


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

st.title("ConfiDesk")
st.caption("Reads customer emails, drafts answers from company docs, and routes low-confidence cases to a human.")

tab_queue, tab_review, tab_escalations, tab_log = st.tabs(
    ["📥 Incoming queue", "✏️ Review drafts", "🚨 Escalations", "📜 Sent log"]
)

# --- Incoming queue: trigger the pipeline on a selected email --------------
with tab_queue:
    st.subheader("Incoming customer emails")
    if not st.session_state.queue:
        st.info("Queue is empty. All caught up.")
    for email in st.session_state.queue:
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{email['subject']}**")
                st.caption(f"From: {email['sender']}")
                st.write(email["body"])
            with col2:
                if st.button("Process", key=f"process_{email['id']}", use_container_width=True):
                    with st.spinner("Read query → RAG search → Generate answer + confidence..."):
                        time.sleep(1.2)  # stand-in for real pipeline latency
                        result = run_pipeline_dummy(email)
                    st.session_state.processed.append(result)
                    st.session_state.queue = [e for e in st.session_state.queue if e["id"] != email["id"]]
                    st.rerun()

# --- Review drafts: Gmail drafts awaiting human approval --------------------
with tab_review:
    st.subheader("Drafts awaiting your approval")
    drafts = [r for r in st.session_state.processed if r["status"] == "pending_review"]
    if not drafts:
        st.info("No drafts waiting for review.")
    for r in drafts:
        with st.container(border=True):
            st.markdown(f"**{r['subject']}**  ·  :blue[Confidence {r['confidence']}/10]")
            st.caption(f"To: {r['sender']}")
            edited = st.text_area("Draft reply", value=r["draft"], key=f"draft_{r['id']}", height=100)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Approve and send", key=f"send_{r['id']}", use_container_width=True):
                    # TODO(Shruti): send_email(r['sender'], edited)  from services/send_email.py
                    r["status"] = "sent"
                    r["draft"] = edited
                    st.success("Sent.")
                    st.rerun()
            with c2:
                st.button("Discard", key=f"discard_{r['id']}", use_container_width=True)

# --- Escalations: low-confidence, sent to WhatsApp --------------------------
with tab_escalations:
    st.subheader("Escalated to the support team via WhatsApp")
    escalations = [r for r in st.session_state.processed if r["status"] == "escalated"]
    if not escalations:
        st.info("No open escalations.")
    for r in escalations:
        with st.container(border=True):
            st.markdown(f"**{r['subject']}**  ·  :orange[Confidence {r['confidence']}/10]")
            st.caption(f"From: {r['sender']}")
            st.write("Notification sent — awaiting a manual reply from the support team.")
            # TODO(Vivanshi): this card reflects notify_team() from services/send_whatsapp.py

# --- Sent log ----------------------------------------------------------------
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
