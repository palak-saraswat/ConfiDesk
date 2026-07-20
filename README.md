# ConfiDesk - AI Customer Support Agent
A safety-first customer support platform that uses AI agents to draft accurate email replies based only on a company's custom brochure, while keeping a human manager in control to approve drafts or step in via WhatsApp alerts if the AI gets confused.



## Features

- **Real‑time inbox fetching** – pulls unread emails directly from Gmail.
- **RAG‑powered reply generation** – uses Google Gemini + your company brochure to produce accurate drafts.
- **Confidence‑based routing** – high‑confidence replies become ***Gmail drafts** (human approval required); low‑confidence cases trigger a ***WhatsApp alert** to the support team.
- **Human review dashboard** – edit, approve, and send drafts or discard them – all from a Streamlit UI.
- **Persistent log** – all processed emails are saved locally, so history survives restarts.



## How It Works
```mermaid
flowchart TD
A[Unread Customer Email]
--> B[Retrieve Company Brochure]
--> C[Gemini Generates Reply]

C --> D{Confidence >= 7}

D -->|Yes| E[Create Gmail Draft]
E --> F[Human Review]
F --> G[Customer Receives Email]

D -->|No| H[WhatsApp Alert]
H --> I[Support Team Reviews Manually]
```


  
## Team & Roles

|         Person         |                Role                |                     Responsibilities               |
|------------------------|------------------------------------|----------------------------------------------------|
|  **Palak Saraswat**    | Orchestrator & LangGraph Architect | Workflow graph (`graph_builder`, `state`, `nodes`) |
|  **Soha**              | AI/ML Engineer                     | Gemini RAG agent, retriever, knowledge base        |
|  **Shruti**            | Backend Developer – Email          | Gmail API (draft, send, inbox fetch)               |
|  **Vivanshi**          | Backend Developer – Notifications  | WhatsApp escalation via Make.com                   |
|  **Anushka Shrotriya** | UI/UX Developer                    | Streamlit dashboard                                |




## Quick Start (Local)

```
git clone <repo-url> && cd ConfiDesk
git checkout dev
pip install -r requirements.txt
cp .env.example .env
# Add credentials.json from Google Cloud (Gmail API)
streamlit run app.py
```

---

## Built with ❤️ by Team ConfiDesk

**Palak Saraswat**   • **Soha**   • **Shruti**   • **Vivanshi**   • **Anushka Shrotriya**

---
