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
    "https://www.googleapis.com/auth/gmail.modify",
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
    """Create a Gmail draft addressed to the customer (not sent)."""
    subject = "Re: Your inquiry to ConfiDesk"
    try:
        service = _get_gmail_service()
        draft_body = _create_message(customer_email, subject, draft_reply)
        service.users().drafts().create(
            userId="me",
            body={"message": draft_body}
        ).execute()
        print(f"[send_email] Draft created for {customer_email}")
        return True
    except Exception as e:
        print(f"[send_email] Failed to create draft: {e}")
        return False


def send_email(recipient: str, subject: str, body: str) -> bool:
    """Send an email immediately via Gmail."""
    try:
        service = _get_gmail_service()
        message = _create_message(recipient, subject, body)
        service.users().messages().send(
            userId="me",
            body=message
        ).execute()
        print(f"[send_email] Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"[send_email] Failed to send email: {e}")
        return False


def fetch_unread_emails(max_results: int = 20) -> list:
    """
    Return a list of unread emails from the Gmail inbox.
    Each dict: id, sender, subject, body (plain text).
    """
    try:
        service = _get_gmail_service()
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            q="is:unread",
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        emails = []

        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()

            headers = msg_data["payload"]["headers"]
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "No Subject"
            )
            sender = next(
                (h["value"] for h in headers if h["name"].lower() == "from"),
                "Unknown"
            )

            body = ""
            payload = msg_data["payload"]
            if "parts" in payload:
                for part in payload["parts"]:
                    if part["mimeType"] == "text/plain":
                        if "data" in part["body"]:
                            body = base64.urlsafe_b64decode(
                                part["body"]["data"]
                            ).decode()
                        break
            else:
                if "data" in payload["body"]:
                    body = base64.urlsafe_b64decode(
                        payload["body"]["data"]
                    ).decode()

            emails.append({
                "id": msg["id"],
                "sender": sender,
                "subject": subject,
                "body": body.strip(),
            })

        return emails

    except Exception as e:
        print(f"[send_email] Failed to fetch emails: {e}")
        return []


def mark_as_read(message_id: str) -> bool:
    """Remove the UNREAD label from a Gmail message."""
    try:
        service = _get_gmail_service()
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()
        return True
    except Exception as e:
        print(f"[send_email] Failed to mark as read: {e}")
        return False