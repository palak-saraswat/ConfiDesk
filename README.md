# ConfiDesk
A safety-first customer support platform that uses AI agents to draft accurate email replies based only on a company's custom brochure, while keeping a human manager in control to approve drafts or step in via WhatsApp alerts if the AI gets confused.

## System Architecture & Workflow
User Submits Email (Via Streamlit UI or Inbox)
               │
               ▼
┌────────────────────────────────────────────────────────┐
│ Node 1: AI Research & Drafting Agent                   │
├────────────────────────────────────────────────────────┤
│ Input: Raw Customer Email                              │
│ Tasks:                                                 │
│  • Read company_brochure.txt context                   │
│  • Cross-verify query facts against brochure           │
│  • Calculate internal confidence score (1-10)          │
│  • Generate polite email response draft                │
│ Output: draft_text, confidence_score                   │
└──────────────────────────────┬─────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────┐
│ Node 2: Conditional Router Node                        │
├────────────────────────────────────────────────────────┤
│ Tasks: Evaluate threshold logic (Score >= 7?)          │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
      (If Score >= 7)             (If Score < 7)
               │                          │
               ▼                          ▼
┌──────────────────────────────┐┌────────────────────────┐
│ Node 3: Manager Dashboard    ││ Node 4: WhatsApp Alert │
├──────────────────────────────┤├────────────────────────┤
│ Output: Renders UI for human ││ Output: Sends Twilio   │
│ approval & secure SMTP send. ││ emergency notification.│
└──────────────────────────────┘└────────────────────────┘
