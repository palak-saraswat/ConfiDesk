# ConfiDesk
A safety-first customer support platform that uses AI agents to draft accurate email replies based only on a company's custom brochure, while keeping a human manager in control to approve drafts or step in via WhatsApp alerts if the AI gets confused.

## System Architecture & Workflow
Customer Email
      │
      ▼
Read Email
      │
      ▼
Search Company Knowledge Base
      │
      ▼
Generate Answer
      │
      ▼
Calculate Confidence Score
      │
      ▼
Is Score ≥ 7 ?
     / \
   Yes  No
   │     │
   ▼     ▼
Create   WhatsApp
Gmail    Notification
Draft
   │
   ▼
Human Reviews
   │
   ▼
Send Email
