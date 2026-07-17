import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64

# Gmail API Scopes (Read and Draft access)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Gmail API Service authenticate aur initialize karne ke liye."""
    creds = None
    # token.pickle credentials store karta hai login session save rakhne ke liye
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def fetch_unread_emails(service):
    """Inbox se unread messages ki list nikalne ke liye."""
    result = service.users().messages().list(userId='me', q='is:unread').execute()
    messages = result.get('messages', [])
    
    email_list = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
        
        email_list.append({
            'id': msg['id'],
            'sender': sender,
            'subject': subject
        })
    return email_list

def create_draft_reply(service, to_email, subject, body):
    """Bina kisi condition ke Gmail me draft create karne ke liye."""
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = f"Re: {subject}"
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        draft = service.users().drafts().create(
            userId='me', 
            body={'message': {'raw': raw_message}}
        ).execute()
        print(f"    [SUCCESS] Draft successfully created (ID: {draft['id']})")
    except Exception as e:
        print(f"    [ERROR] Failed to create draft: {e}")

def main():
    # 1. Gmail API Service setup
    service = get_gmail_service()
    
    print("Fetching unread emails...")
    emails = fetch_unread_emails(service)
    
    if not emails:
        print("No unread emails found.")
        return

    print(f"Found {len(emails)} unread email(s). Processing...")

    # 2. Straightforward Loop: No AI, No Confidence Check, No Context Analysis
    for email in emails:
        print(f"\nProcessing Email from: {email['sender']}")
        
        # Ek default generic confirmation text template
        default_reply_body = (
            "Hello,\n\n"
            "Thank you for reaching out. We have received your email "
            "and our team will get back to you shortly.\n\n"
            "Best regards,\n"
            "Customer Support"
        )
        
        # Direct Call to Gmail Workflow
        create_draft_reply(
            service=service,
            to_email=email['sender'],
            subject=email['subject'],
            body=default_reply_body
        )

if __name__ == '__main__':
    main()