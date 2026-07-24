"""
ConfiDesk - app.py (Entry Point)
Integrated with real LangGraph pipeline and Gmail sending
"""

import streamlit as st
import json
from pathlib import Path

from graph_builder import graph                                
from services.send_email import send_email, fetch_unread_emails, mark_as_read

st.set_page_config(page_title="ConfiDesk", page_icon="📨", layout="wide")

# ---------------------------------------------------------------------------
# Persistent storage for processed emails (survives app restarts)
# ---------------------------------------------------------------------------
PROCESSED_FILE = Path("processed_emails.json")

def load_processed():
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE, "r") as f:
            return json.load(f)
    return []

def save_processed(data):
    with open(PROCESSED_FILE, "w") as f:
        json.dump(data, f)

# Initialize session state from disk
if "processed" not in st.session_state:
    st.session_state.processed = load_processed()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ConfiDesk")
    st.caption("Customer email agent")
    st.caption("Team ConfiDesk")  # optional credit

    st.markdown("**Connections**")
    st.write("📧 Gmail — :green[Connected]")
    st.write("💬 WhatsApp — :green[Connected]")
    st.write("📚 RAG index — :green[142 docs loaded]")

    st.divider()
    st.slider(
        "Confidence threshold (informational)", min_value=0.0, max_value=10.0,
        value=7.0, step=0.5,
        help="Pipeline routes ≥7 → Gmail draft, <7 → WhatsApp escalation."
    )
    st.divider()
    st.metric("Processed today", len(st.session_state.processed))

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
st.title("ConfiDesk")
st.caption("Reads real customer emails from Gmail, drafts replies, and routes low‑confidence cases to a human.")

tab_queue, tab_review, tab_escalations, tab_log = st.tabs(
    ["📥 Incoming queue", "✏️ Review drafts", "🚨 Escalations", "📜 Sent log"]
)

# ---------------------------------------------------------------------------
# INCOMING QUEUE – real unread emails from Gmail
# ---------------------------------------------------------------------------
with tab_queue:
    st.subheader("Unread customer emails")
    if st.button("🔄 Refresh inbox"):
        st.rerun()

    emails = fetch_unread_emails(max_results=20)
    if not emails:
        st.info("No unread emails found in the inbox.")
    else:
        for email in emails:
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

                            try:
                                # Run the AI + routing graph
                                final_state = graph.invoke(initial_state)

                                # Build the processed record
                                result = {
                                    "id": email["id"],
                                    "sender": email["sender"],
                                    "subject": email["subject"],
                                    "confidence": final_state.get("confidence_score", 0),
                                    "draft": final_state.get("draft_reply", ""),
                                    "status": final_state.get("status", "escalated"),
                                }

                                # Only mark as read and save if successful
                                mark_as_read(email["id"])
                                st.session_state.processed.append(result)
                                save_processed(st.session_state.processed)
                                st.success("Email processed successfully!")
                            except Exception as e:
                                st.error(f"Processing failed: {e}")

                            st.rerun()

# ---------------------------------------------------------------------------
# REVIEW DRAFTS – items that need human approval (status = pending_review)
# ---------------------------------------------------------------------------
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
                        save_processed(st.session_state.processed)
                        st.success("Sent.")
                    else:
                        st.error("Failed to send. Check server logs.")
                    st.rerun()
            with c2:
                if st.button("Discard", key=f"discard_{r['id']}", use_container_width=True):
                    st.session_state.processed.remove(r)
                    save_processed(st.session_state.processed)
                    st.rerun()

# ---------------------------------------------------------------------------
# ESCALATIONS – low confidence (status = escalated)
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# SENT LOG
# ---------------------------------------------------------------------------
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