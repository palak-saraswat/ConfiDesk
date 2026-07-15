import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

def send_low_confidence_alert(customer_email: str, confidence_score: int, draft_reply: str, status: str = "escalated") -> bool:
    """
    Sends a POST request to the Make.com webhook to trigger a WhatsApp
    alert to the helpdesk manager when AI confidence is below threshold.
    """
    if not WEBHOOK_URL:
        raise ValueError("MAKE_WEBHOOK_URL not found in environment variables.")

    payload = {
        "customer_email": customer_email,
        "confidence_score": confidence_score,
        "draft_reply": draft_reply,
        "status": status,
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"[send_whatsapp] Failed to send alert: {e}")
        return False


if __name__ == "__main__":
    success = send_low_confidence_alert(
        customer_email="test.customer@example.com",
        confidence_score=4,
        draft_reply="I'm not fully sure about our refund policy after 30 days...",
        status="escalated"
    )
    print("Alert sent!" if success else "Alert failed.")