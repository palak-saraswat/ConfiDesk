import os
import base64
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
]

TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def _get_gmail_service():
    """Authenticate and return a Gmail API service instance."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _create_message(recipient: str, subject: str, body: str) -> dict:
    """Create a Gmail API compatible message."""
    mime_msg = MIMEText(body)
    mime_msg["to"] = recipient
    mime_msg["subject"] = subject
    raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()
    return {"raw": raw}


def send_email_draft(customer_email: str, draft_reply: str) -> bool:
    """
    Create a Gmail draft addressed to the customer.
    The draft is not sent – it sits in the Drafts folder for human review.
    """
    subject = "Re: Your inquiry to ConfiDesk"
    try:
        service = _get_gmail_service()
        draft_body = _create_message(customer_email, subject, draft_reply)
        service.users().drafts().create(userId="me", body={"message": draft_body}).execute()
        print(f"[send_email] Draft created for {customer_email}")
        return True
    except Exception as e:
        print(f"[send_email] Failed to create draft: {e}")
        return False


def send_email(recipient: str, subject: str, body: str) -> bool:
    """
    Sends an email immediately via Gmail.
    Used when the human clicks “Approve and send” in the UI.
    """
    try:
        service = _get_gmail_service()
        message = _create_message(recipient, subject, body)
        service.users().messages().send(userId="me", body=message).execute()
        print(f"[send_email] Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"[send_email] Failed to send email: {e}")
        return False


# Quick test (optional)
if __name__ == "__main__":
    send_email_draft("test@example.com", "This is a draft reply.")
    send_email("test@example.com", "Test subject", "This is a real sent email.")