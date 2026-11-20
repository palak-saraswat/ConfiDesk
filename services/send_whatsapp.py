
import os
import requests

from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

CONFIDENCE_THRESHOLD = 7


def send_low_confidence_alert(
    customer_email: str,
    confidence_score: int,
    draft_reply: str,
    status: str = "escalated",
) -> bool:
    """
    Sends a low-confidence escalation alert to Make.com.

    Make.com will forward the alert through Twilio WhatsApp
    to the designated support team member.
    """

    # Safety check: only scores below 7 can trigger alerts.
    if confidence_score >= CONFIDENCE_THRESHOLD:
        print(
            "[WhatsApp] Confidence score is 7 or above. "
            "Notification skipped."
        )
        return False

    if not WEBHOOK_URL:
        print(
            "[WhatsApp] ERROR: MAKE_WEBHOOK_URL missing "
            "from environment. Notification skipped."
        )
        return False

    payload = {
        "customer_email": customer_email,
        "confidence_score": confidence_score,
        "draft_reply": draft_reply,
        "status": status,
    }

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        print(
            "[WhatsApp] Alert successfully delivered "
            "to Make.com webhook."
        )

        return True

    except requests.exceptions.RequestException as e:
        print(f"[WhatsApp] Webhook request failed: {e}")
        return False


if __name__ == "__main__":

    # Test case: confidence score 4 should trigger an alert.
    success = send_low_confidence_alert(
        customer_email="test.customer@example.com",
        confidence_score=4,
        draft_reply=(
            "I'm not fully sure about our refund policy "
            "after 30 days..."
        ),
        status="escalated",
    )

    print(
        "Alert triggered successfully!"
        if success
        else "Alert failed or was skipped."
    )
