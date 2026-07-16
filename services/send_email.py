import os
import base64
import logging
import re
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Google Library Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 1. Configure the Production Logging System
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(filename)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 2. Consolidated Scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose"
]

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

# =================================================
# XYZ Company Pvt. Ltd. - Integrated Knowledge Base
# =================================================
KNOWLEDGE_BASE = {
    "hours": (
        "Business Hours:\n"
        "- Monday to Friday: 9:00 AM – 6:00 PM IST\n"
        "- Saturday: 10:00 AM – 2:00 PM IST\n"
        "- Sunday: Closed"
    ),
    "support": (
        "Customer Support Contact Information:\n"
        "- Email: support@xyzcompany.com\n"
        "- Phone: +91-9876543210\n"
        "- Average Response Time: Within 24 business hours."
    ),
    "services": (
        "Services Offered by XYZ Company:\n"
        "• Web Application Development & Scalable Responsive Websites\n"
        "• Mobile Application Development (Android, iOS, & Cross-Platform)\n"
        "• Artificial Intelligence Solutions & Agentic AI Systems\n"
        "• AI Chatbot Development\n"
        "• Cloud Deployment (AWS, Microsoft Azure, and Google Cloud Platform)\n"
        "• API Development\n"
        "• Business Process Automation\n"
        "• Software Consulting"
    ),
    "payments": (
        "Payment Policy:\n"
        "- 50% advance payment before project initiation.\n"
        "- Remaining 50% after successful project completion.\n"
        "- Accepted Payment Methods: Bank Transfer, UPI, and Credit Card."
    ),
    "refunds": (
        "Refund & Project Cancellation Policy:\n"
        "- Refund Eligibility: Available within 30 calendar days of payment, provided project development has not started.\n"
        "- Mid-Development Requests: Evaluated individually; cancellation charges depend dynamically on work completed.\n"
        "- Completed Projects: Strictly non-refundable."
    ),
    "tech_support": (
        "Complimentary Technical Support:\n"
        "Every completed project includes 90 days of complimentary technical support covering:\n"
        "- Bug fixes\n"
        "- Minor software updates\n"
        "- Deployment assistance\n"
        "* Note: New feature requests are treated as separate development work."
    ),
    "maintenance": (
        "Long-Term Maintenance Plans & Response Times:\n"
        "1. Basic Plan: Includes Email support & Monthly maintenance (Response within 24 business hours).\n"
        "2. Professional Plan: Includes Priority support, Weekly monitoring & Performance optimization (Response within 8 business hours).\n"
        "3. Enterprise Plan: Includes a Dedicated support engineer, 24×7 monitoring & SLA-based support (Response within 2 business hours)."
    ),
    "security": (
        "Security, Privacy, & Data Retention:\n"
        "- Core Practices: Data encryption, secure cloud infrastructure, role-based access control, and regular security audits.\n"
        "- Privacy: Customer information is used strictly to provide requested services and never shared without permission.\n"
        "- Data Retention: Customer records are securely retained for exactly one year after project completion."
    )
}


def get_gmail_service():
    """Authenticates the user using OAuth 2.0 and returns an authorized Gmail service client."""
    creds = None
    try:
        if os.path.exists(TOKEN_PATH):
            logger.info("Attempting to load saved token.json...")
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid or not creds.has_scopes(SCOPES):
            if creds and creds.expired and creds.refresh_token and creds.has_scopes(SCOPES):
                logger.warning("Access token expired. Attempting silent refresh...")
                try:
                    creds.refresh(Request())
                    logger.info("Token refreshed successfully.")
                except Exception as refresh_err:
                    logger.error(f"Silent refresh failed: {refresh_err}. Re-authenticating...")
                    creds = None
            
            if not creds or not creds.valid or not creds.has_scopes(SCOPES):
                logger.info("No valid token or insufficient permissions. Opening browser for authorization...")
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(
                        f"Missing '{CREDENTIALS_PATH}' in the root directory. Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())
                logger.info("Updated token.json saved securely with complete scopes.")

        return build("gmail", "v1", credentials=creds)
    except Exception as e:
        logger.error(f"Critical error during Gmail service initialization: {e}")
        raise


def evaluate_query_and_respond(subject: str, snippet: str) -> tuple:
    """Scans emails against the brochure text keywords.
    
    Returns:
        tuple: (confidence_score, reply_body)
    """
    combined_text = f"{subject} {snippet}".lower()
    
    # Matching keyword mappings extracted from brochure guidelines
    if any(k in combined_text for k in ["hour", "time", "open", "timing", "saturday", "sunday", "operational"]):
        return 9, f"Here are our operational details:\n\n{KNOWLEDGE_BASE['hours']}"
        
    elif any(k in combined_text for k in ["support", "email", "phone", "contact", "call", "reach", "response time"]):
        # Route to specific maintenance plan answer if specific tiers are called out
        if any(m in combined_text for m in ["plan", "basic", "professional", "enterprise", "sla"]):
            return 9, f"For extended long-term support systems, we offer structured tiers:\n\n{KNOWLEDGE_BASE['maintenance']}"
        return 9, f"You can reach out directly via the following methods:\n\n{KNOWLEDGE_BASE['support']}"
        
    elif any(k in combined_text for k in ["build", "website", "app", "mobile", "develop", "ai", "agentic", "bot", "cloud", "aws", "azure", "gcp", "android", "ios"]):
        return 9, f"Here is an overview of our custom capabilities:\n\n{KNOWLEDGE_BASE['services']}"
        
    elif any(k in combined_text for k in ["pay", "advance", "cost", "price", "credit card", "upi", "bank", "method"]):
        return 9, f"Here is our standard operational payment framework:\n\n{KNOWLEDGE_BASE['payments']}"
        
    elif any(k in combined_text for k in ["refund", "cancel", "money back", "return", "cancellation"]):
        return 9, f"Regarding policy adjustments, please find our terms below:\n\n{KNOWLEDGE_BASE['refunds']}"
        
    elif any(k in combined_text for k in ["free support", "complimentary", "bug", "fix", "update", "90 days"]):
        return 9, f"Every completed project includes a standard care tier:\n\n{KNOWLEDGE_BASE['tech_support']}"
        
    elif any(k in combined_text for k in ["maintenance", "sla", "monitoring"]):
        return 9, f"For extended long-term support systems, we offer structured tiers:\n\n{KNOWLEDGE_BASE['maintenance']}"
        
    elif any(k in combined_text for k in ["secure", "encryption", "privacy", "audit", "data", "retention", "third parties"]):
        return 9, f"We treat structural protection protocols with high priority:\n\n{KNOWLEDGE_BASE['security']}"
    
    # Anti-Hallucination Safe Default: Mark for human validation
    return 4, "I am tracking no matching information within the base document guidelines. Transferring for human validation review."


def fetch_latest_emails(service, max_results=5) -> list:
    """Fetches incoming metadata patterns for matching evaluation passes."""
    logger.info(f"Fetching your latest {max_results} emails...")
    try:
        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])
        
        email_list = []
        if not messages:
            logger.info("No incoming messages detected.")
            return email_list

        for msg in messages:
            full_msg = service.users().messages().get(userId="me", id=msg["id"]).execute()
            snippet = full_msg.get("snippet", "No preview available.")
            headers = full_msg.get("payload", {}).get("headers", [])
            
            subject = "No Subject"
            sender = "Unknown Sender"
            for header in headers:
                if header["name"] == "Subject":
                    subject = header["value"]
                elif header["name"] == "From":
                    sender = header["value"]
            
            email_list.append({
                "id": msg["id"],
                "sender": sender,
                "subject": subject,
                "snippet": snippet
            })
        return email_list
    except HttpError as http_err:
        logger.error(f"API Error fetching emails: {http_err}")
        return []


def create_draft_reply(service, to_email: str, subject: str, body_text: str) -> dict:
    """Encodes and registers structured text strings into system draft locations."""
    logger.info(f"Initiating draft creation for: {to_email}")
    try:
        formatted_body = (
            f"Dear Customer,\n\n"
            f"{body_text}\n\n"
            f"If you have additional specific configurations, please feel free to ask.\n\n"
            f"Best regards,\n"
            f"XYZ Company Support Assistant Team"
        )
        
        mime_message = MIMEText(formatted_body)
        mime_message["to"] = to_email
        mime_message["from"] = "me"
        # Standardize matching response threading title string format
        if not subject.lower().startswith("re:"):
            mime_message["subject"] = f"Re: {subject}"
        else:
            mime_message["subject"] = subject

        raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode("utf-8")
        draft_body = {"message": {"raw": raw_message}}

        draft = service.users().drafts().create(userId="me", body=draft_body).execute()
        logger.info(f"Draft successfully created! Draft ID: {draft['id']}")
        return draft
    except Exception as exc:
        logger.error(f"Unexpected system error during draft creation: {exc}")
        return {}


def main():
    load_dotenv()
    service = get_gmail_service()
    emails = fetch_latest_emails(service, max_results=5)
    
    if not emails:
        print("\nYour inbox is empty. Send a test email containing phrases like 'refund policy' or 'business hours' to check execution metrics.")
        return

    print("\n" + "="*60)
    print("         XYZ COMPANY KNOWLEDGE BASE INBOX ROUTER")
    print("="*60)
    
    for idx, email in enumerate(emails, 1):
        print(f"\n[{idx}] Processing Email From: {email['sender']}")
        print(f"    Subject: {email['subject']}")
        print(f"    Preview: {email['snippet']}")
        
        # Calculate confidence tracking metrics using structural rules
        score, dynamic_reply = evaluate_query_and_respond(email['subject'], email['snippet'])
        print(f"    Calculated Confidence Score: {score}/10")
        
        if score >= 7:
            print("    [Confidence Threshold Met] Generating automated draft workflow response...")
            create_draft_reply(service, email['sender'], email['subject'], dynamic_reply)
        else:
            print("    [WARNING - Low Confidence] Score below 7. Route assigned for manual human evaluation flag.")
        print("-" * 60)


if __name__ == "__main__":
    main()